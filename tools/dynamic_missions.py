#!/usr/bin/env python3
"""Build and serve configuration-driven War Thunder custom missions."""

from __future__ import annotations

import argparse
import copy
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time
import tomllib
from typing import Any
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from tools import build_variants as variants


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_DIR = ROOT / "config"
DEFAULT_OUTPUT_DIR = ROOT / "build" / "dynamic"
DYNAMIC_PREFIX = "/wt/missions/dynamic/"


class ConfigError(ValueError):
    """Raised when a dynamic mission profile is invalid."""


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge mappings; scalar/list values replace their base value."""
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ConfigError(f"Could not read {path}: {error}") from error


def load_profiles(config_dir: Path = DEFAULT_CONFIG_DIR) -> dict[str, dict[str, Any]]:
    base_path = config_dir / "base.toml"
    maps_dir = config_dir / "maps"
    base = read_toml(base_path)
    profiles: dict[str, dict[str, Any]] = {}
    for path in sorted(maps_dir.glob("*.toml")):
        profile = deep_merge(base, read_toml(path))
        mission = profile.get("mission", {})
        if not mission.get("enabled", True):
            continue
        slug = mission.get("slug")
        adapter = mission.get("adapter")
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
            raise ConfigError(f"{path}: mission.slug must be a URL-safe lowercase slug")
        if slug in profiles:
            raise ConfigError(f"Duplicate mission slug: {slug}")
        if adapter not in {"archipelago-2018", "south-eastern-city"}:
            raise ConfigError(f"{path}: unsupported mission.adapter {adapter!r}")
        profile["_config_path"] = str(path)
        profiles[slug] = profile
    if not profiles:
        raise ConfigError(f"No enabled map profiles found in {maps_dir}")
    return profiles


def set_metadata(text: str, title: str, description: str) -> str:
    text, title_count = re.subn(
        r'(?m)^(\s*)locName:t(?:\s*=\s*|=)"[^"]*"$',
        rf'\1locName:t="{title}"',
        text,
        count=1,
    )
    text, description_count = re.subn(
        r'(?m)^(\s*)locDesc:t(?:\s*=\s*|=)"[^"]*"$',
        rf'\1locDesc:t="{description}"',
        text,
        count=1,
    )
    if (title_count, description_count) != (1, 1):
        raise ConfigError("Could not replace mission title and description")
    return text


def prepare_south_eastern_source() -> str:
    text = variants.flatten_southeastern_imports(
        variants.SOUTHEASTERN_CITY_SOURCE.read_text(encoding="utf-8")
    )
    text = variants.prune_ranked_blocks(text, mission_rank=37)
    return variants.quote_plus_sign_storage_templates(text)


def apply_archipelago_defenses(text: str, config: dict[str, Any]) -> str:
    defenses = config["defenses"]
    strategic_mode = defenses["strategic_sams"]
    if strategic_mode == "silent":
        text = variants.disable_sam_channels(text)
    elif strategic_mode == "removed":
        text = variants.remove_object_groups_with_templates(
            text, ("sam_site_s300", "sam_site_sampt")
        )
    elif strategic_mode != "stock":
        raise ConfigError(f"Unsupported strategic_sams mode: {strategic_mode}")

    hq11_mode = defenses["hq11_mode"]
    if hq11_mode == "range_limited":
        text = variants.override_team1_airfield_roster(
            text, float(defenses["hq11_range_km"]) * 1000.0
        )
    elif hq11_mode == "silent":
        text = variants.override_team1_airfield_roster(
            text, hq11_threat_radius=0.0, hq11_ammo=0, hq11_radar_managed=False
        )
    elif hq11_mode != "stock":
        raise ConfigError(f"Unsupported hq11_mode: {hq11_mode}")
    return text


def apply_south_eastern_defenses(text: str, config: dict[str, Any]) -> str:
    defenses = config["defenses"]
    strategic_mode = defenses["strategic_sams"]
    if strategic_mode == "silent":
        text = variants.disable_pretty_sam_channels(text)
    elif strategic_mode == "removed":
        text = variants.remove_pretty_object_groups_with_templates(
            text, ("sam_site_s300", "sam_site_sampt")
        )
    elif strategic_mode != "stock":
        raise ConfigError(f"Unsupported strategic_sams mode: {strategic_mode}")

    hq11_mode = defenses["hq11_mode"]
    if hq11_mode == "range_limited":
        text = variants.override_pretty_team1_airfields(
            text, float(defenses["hq11_range_km"]) * 1000.0
        )
    elif hq11_mode == "silent":
        raise ConfigError("South-Eastern City does not yet support silent HQ-11 mode")
    elif hq11_mode != "stock":
        raise ConfigError(f"Unsupported hq11_mode: {hq11_mode}")
    return variants.compact_scalar_syntax(text)


def apply_rules_and_spawns(text: str, config: dict[str, Any]) -> str:
    rules = config["rules"]
    text = variants.set_player_respawn_delay(text, int(rules["respawn_seconds"]))
    for setting, key in (
        ("isAirplanesAllowed", "aircraft"),
        ("isHelicoptersAllowed", "helicopters"),
        ("isShipsAllowed", "naval"),
        ("isTanksAllowed", "tanks"),
    ):
        text = variants.set_allowed_unit_type(text, setting, bool(rules[key]))

    ship_range_km = float(config["defenses"].get("missile_ship_range_km", 0.0))
    if ship_range_km > 0:
        text = variants.limit_missile_ship_engagements(text, ship_range_km * 1000.0)

    spawns = config["spawns"]
    aircraft = spawns["aircraft"]
    if aircraft.get("enabled", False):
        placements = {
            suffix: (
                float(values["altitude_m"]),
                float(values["rear_offset_m"]),
            )
            for suffix, values in aircraft.get("fields", {}).items()
        }
        if not placements:
            raise ConfigError("Aircraft spawns are enabled but no fields are configured")
        text = variants.add_airfield_air_spawns(
            text,
            placements,
            tuple(aircraft.get("main_forward_fields", [])),
            float(aircraft.get("main_forward_fraction", 0.5)),
        )

    helicopters = spawns["helicopters"]
    if helicopters.get("enabled", False):
        text = variants.add_frontal_helicopter_spawns(
            text,
            tuple(helicopters.get("fields", ["01", "02", "03"])),
            float(helicopters.get("altitude_agl_m", 300.0)),
            -float(helicopters.get("forward_from_field_m", 0.0)),
        )

    naval = spawns["naval"]
    if naval.get("enabled", False):
        text = variants.add_carrier_forward_naval_spawns(
            text, float(naval.get("forward_from_carrier_m", 3000.0))
        )
    return text


def validate_profile(config: dict[str, Any]) -> None:
    rules = config["rules"]
    spawns = config["spawns"]
    for unit_key, spawn_key in (
        ("aircraft", "aircraft"),
        ("helicopters", "helicopters"),
        ("naval", "naval"),
    ):
        if spawns[spawn_key].get("enabled", False) and not rules[unit_key]:
            raise ConfigError(f"{spawn_key} spawns are enabled while {unit_key} is disabled")
    if int(rules["respawn_seconds"]) < 0:
        raise ConfigError("rules.respawn_seconds cannot be negative")
    if float(config["defenses"].get("hq11_range_km", 0.0)) < 0:
        raise ConfigError("defenses.hq11_range_km cannot be negative")


def build_mission(config: dict[str, Any]) -> str:
    validate_profile(config)
    adapter = config["mission"]["adapter"]
    if adapter == "archipelago-2018":
        text = variants.ARCHIPELAGO_SOURCE.read_text(encoding="utf-8")
        text = apply_archipelago_defenses(text, config)
    elif adapter == "south-eastern-city":
        text = apply_south_eastern_defenses(prepare_south_eastern_source(), config)
    else:
        raise ConfigError(f"Unsupported adapter: {adapter}")
    text = apply_rules_and_spawns(text, config)
    text = set_metadata(
        text,
        str(config["mission"]["title"]),
        str(config["mission"]["description"]),
    )
    variants.assert_balanced(text)
    return text


def build_all(
    config_dir: Path = DEFAULT_CONFIG_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    selected: set[str] | None = None,
) -> dict[str, bytes]:
    profiles = load_profiles(config_dir)
    if selected:
        missing = selected - profiles.keys()
        if missing:
            raise ConfigError(f"Unknown map slug(s): {', '.join(sorted(missing))}")
        profiles = {slug: profile for slug, profile in profiles.items() if slug in selected}
    output_dir.mkdir(parents=True, exist_ok=True)
    built: dict[str, bytes] = {}
    for slug, profile in profiles.items():
        payload = build_mission(profile).encode("utf-8")
        destination = output_dir / f"{slug}.blk"
        temporary = destination.with_suffix(".blk.tmp")
        temporary.write_bytes(payload)
        temporary.replace(destination)
        built[slug] = payload
    return built


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()[:12]


class MissionStore:
    def __init__(self, config_dir: Path, output_dir: Path):
        self.config_dir = config_dir
        self.output_dir = output_dir
        self._lock = threading.Lock()
        self._missions: dict[str, bytes] = {}
        self.fetch_event = threading.Event()

    def rebuild(self) -> dict[str, bytes]:
        missions = build_all(self.config_dir, self.output_dir)
        with self._lock:
            self._missions = missions
        return missions

    def get(self, slug: str) -> bytes | None:
        with self._lock:
            return self._missions.get(slug)

    def slugs(self) -> list[str]:
        with self._lock:
            return sorted(self._missions)


def make_handler(store: MissionStore) -> type[BaseHTTPRequestHandler]:
    class MissionHandler(BaseHTTPRequestHandler):
        server_version = "WTMissionServer/1.0"

        def do_HEAD(self) -> None:  # noqa: N802 - required HTTP handler name
            self._serve(send_body=False)

        def do_GET(self) -> None:  # noqa: N802 - required HTTP handler name
            self._serve(send_body=True)

        def _serve(self, send_body: bool) -> None:
            path = unquote(urlparse(self.path).path)
            if path == DYNAMIC_PREFIX:
                body = ("\n".join(f"{slug}.blk" for slug in store.slugs()) + "\n").encode()
                self._respond(200, body, "text/plain; charset=utf-8", send_body)
                return
            if not path.startswith(DYNAMIC_PREFIX) or not path.endswith(".blk"):
                self._respond(404, b"Not found\n", "text/plain", send_body)
                return
            slug = path[len(DYNAMIC_PREFIX) : -4]
            if "/" in slug or not slug:
                self._respond(404, b"Not found\n", "text/plain", send_body)
                return
            payload = store.get(slug)
            if payload is None:
                self._respond(404, b"Unknown mission\n", "text/plain", send_body)
                return
            self._respond(200, payload, "text/plain; charset=utf-8", send_body)
            if send_body:
                store.fetch_event.set()
                print(
                    f"Downloaded: {slug}.blk ({len(payload):,} bytes, sha256 {digest(payload)})",
                    flush=True,
                )

        def _respond(
            self, status: int, body: bytes, content_type: str, send_body: bool
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if send_body:
                self.wfile.write(body)

        def log_message(self, fmt: str, *args: object) -> None:
            print(f"HTTP {self.address_string()}: {fmt % args}", flush=True)

    return MissionHandler


def tailscale_dns_name() -> str:
    result = subprocess.run(
        ["tailscale", "status", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    dns_name = str(data.get("Self", {}).get("DNSName", "")).rstrip(".")
    if not dns_name:
        raise RuntimeError("Tailscale did not report a DNS name")
    return dns_name


def public_dns_addresses(dns_name: str) -> list[str]:
    """Resolve through a public recursive resolver, bypassing Tailscale MagicDNS."""
    request = Request(
        f"https://dns.google/resolve?name={dns_name}&type=A",
        headers={"Accept": "application/dns-json", "User-Agent": "wtmission/1.0"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            result = json.load(response)
    except (OSError, TimeoutError, ValueError):
        return []
    return [
        answer["data"]
        for answer in result.get("Answer", [])
        if answer.get("type") in (1, 28) and isinstance(answer.get("data"), str)
    ]


def wait_for_public_dns(
    dns_name: str, process: subprocess.Popen[str], timeout: float
) -> list[str]:
    deadline = time.monotonic() + timeout
    print(
        f"Waiting for {dns_name} to appear in public DNS "
        f"(first activation can take up to {timeout / 60:g} minutes)...",
        flush=True,
    )
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Tailscale Funnel exited before public DNS was ready")
        addresses = public_dns_addresses(dns_name)
        if addresses:
            print(f"Public DNS ready: {', '.join(addresses)}", flush=True)
            return addresses
        time.sleep(5)
    raise RuntimeError(
        f"Tailscale Funnel started, but {dns_name} did not appear in public DNS "
        f"within {timeout:g} seconds"
    )


def start_tailscale_funnel(
    port: int, dns_timeout: float
) -> tuple[subprocess.Popen[str], str]:
    dns_name = tailscale_dns_name()
    process = subprocess.Popen(
        ["tailscale", "funnel", str(port)],
        text=True,
    )
    time.sleep(1.5)
    if process.poll() is not None:
        raise RuntimeError("Tailscale Funnel exited before the server was published")
    try:
        wait_for_public_dns(dns_name, process, dns_timeout)
    except Exception:
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
        raise
    return process, f"https://{dns_name}"


def print_built(missions: dict[str, bytes], base_url: str | None = None) -> None:
    for slug, payload in sorted(missions.items()):
        target = f"{DYNAMIC_PREFIX}{slug}.blk"
        if base_url:
            target = base_url.rstrip("/") + target
        print(f"{target}  {len(payload):,} bytes  sha256:{digest(payload)}")
        if target.startswith("https://"):
            print(f"  War Thunder (keep HTTPS): {target}")


def watched_state(config_dir: Path) -> tuple[tuple[str, int, int], ...]:
    paths = list(config_dir.rglob("*.toml"))
    paths.extend((variants.ARCHIPELAGO_SOURCE, variants.SOUTHEASTERN_CITY_SOURCE))
    state: list[tuple[str, int, int]] = []
    for path in sorted(paths):
        try:
            stat = path.stat()
        except FileNotFoundError:
            state.append((str(path), -1, -1))
        else:
            state.append((str(path), stat.st_mtime_ns, stat.st_size))
    return tuple(state)


def watch_and_rebuild(store: MissionStore, stop: threading.Event) -> None:
    previous = watched_state(store.config_dir)
    while not stop.wait(1.0):
        current = watched_state(store.config_dir)
        if current == previous:
            continue
        previous = current
        try:
            missions = store.rebuild()
        except Exception as error:  # Keep serving the last known-good build.
            print(f"Rebuild failed; still serving previous missions: {error}", flush=True)
            continue
        print("Configuration changed; rebuilt missions:", flush=True)
        print_built(missions)


def command_build(args: argparse.Namespace) -> int:
    selected = set(args.map) if args.map else None
    missions = build_all(args.config_dir, args.output_dir, selected)
    print_built(missions)
    return 0


def command_list(args: argparse.Namespace) -> int:
    profiles = load_profiles(args.config_dir)
    for slug, profile in profiles.items():
        defenses = profile["defenses"]
        print(
            f"{slug}: {profile['mission']['adapter']}; "
            f"strategic SAMs={defenses['strategic_sams']}; "
            f"HQ-11={defenses['hq11_mode']} ({profile['_config_path']})"
        )
    return 0


def command_serve(args: argparse.Namespace) -> int:
    store = MissionStore(args.config_dir, args.output_dir)
    missions = store.rebuild()
    server = ThreadingHTTPServer((args.bind, args.port), make_handler(store))
    actual_port = server.server_address[1]
    funnel: subprocess.Popen[str] | None = None
    base_url = f"http://{args.bind}:{actual_port}"
    if args.public == "tailscale":
        funnel, base_url = start_tailscale_funnel(actual_port, args.funnel_dns_timeout)

    print("Available missions:")
    print_built(missions, base_url)
    print("Press Ctrl+C to stop. The public link works only while this process is running.")

    watch_stop = threading.Event()
    watcher: threading.Thread | None = None
    if args.watch:
        watcher = threading.Thread(
            target=watch_and_rebuild, args=(store, watch_stop), daemon=True
        )
        watcher.start()
        print("Watching configuration files; valid edits are rebuilt in place.")

    if args.exit_after_fetch is not None:
        def stop_after_fetch() -> None:
            store.fetch_event.wait()
            if args.exit_after_fetch > 0:
                time.sleep(args.exit_after_fetch)
            print("Mission fetched; stopping server.", flush=True)
            server.shutdown()

        threading.Thread(target=stop_after_fetch, daemon=True).start()

    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        watch_stop.set()
        if watcher is not None:
            watcher.join(timeout=2)
        server.server_close()
        if funnel is not None and funnel.poll() is None:
            funnel.send_signal(signal.SIGINT)
            try:
                funnel.wait(timeout=5)
            except subprocess.TimeoutExpired:
                funnel.terminate()
    return 0


def parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--config-dir", type=Path, default=DEFAULT_CONFIG_DIR, help="configuration root"
    )
    common.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="generated mission directory"
    )

    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build", parents=[common], help="build configured missions")
    build.add_argument("--map", action="append", help="build only this map slug")
    build.set_defaults(func=command_build)

    listing = commands.add_parser("list", parents=[common], help="list configured maps")
    listing.set_defaults(func=command_list)

    serve = commands.add_parser("serve", parents=[common], help="build and serve every map")
    serve.add_argument("--bind", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--public", choices=("none", "tailscale"), default="none")
    serve.add_argument(
        "--funnel-dns-timeout",
        type=float,
        default=600.0,
        metavar="SECONDS",
        help="wait this long for first-time Funnel public DNS (default: 600)",
    )
    serve.add_argument(
        "--watch",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="rebuild in place when a config or source mission changes (default: enabled)",
    )
    serve.add_argument(
        "--exit-after-fetch",
        nargs="?",
        type=float,
        const=0.0,
        metavar="SECONDS",
        help="stop after the first successful mission GET, optionally after a grace period",
    )
    serve.set_defaults(func=command_serve)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (
        ConfigError,
        KeyError,
        OSError,
        RuntimeError,
        ValueError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
