# War Thunder custom missions

Version-controlled custom missions and variants for War Thunder.

## Missions

- [Nuclear Escalation — Archipelago (2018)](missions/ne-archipelago-2018/README.md)
- [Nuclear Escalation — Southeastern City](missions/ne-southeastern-city/README.md)

The `.blk` links in each mission folder are intended for War Thunder's
**Missions by URL** menu. If the game rejects a URL, remove the `https://`
prefix before pasting it.

## Development

Regenerate maintained variants with:

```sh
python3 tools/build_variants.py
```

`source.blk` is kept unchanged. Generated variants carry a visible title tag
so the loaded version can be verified in game.

## Dynamic mission builder

The repository also includes configuration-driven mission generation. Shared
defaults live in [`config/base.toml`](config/base.toml), and each enabled map
has a deep-merged override in [`config/maps`](config/maps).

Build every configured map:

```sh
./wtmission build
```

Serve every map locally:

```sh
./wtmission serve
```

Serve them publicly through the machine's Tailscale Funnel:

```sh
./wtmission serve --public tailscale
```

On first activation, the launcher waits until the Tailscale hostname is visible
through public DNS before presenting it as ready. This matters because the same
name can start working through private MagicDNS several minutes before an
external service such as War Thunder can resolve it.

The public paths remain predictable across rebuilds:

```text
/wt/missions/dynamic/archipelago-2018.blk
/wt/missions/dynamic/south-eastern-city.blk
```

The server sends no-cache headers and logs each successful mission download.
Configuration changes are rebuilt in place by default, without changing any
URL; an invalid edit leaves the last valid build online. The server runs until
Ctrl+C by default. Pass `--exit-after-fetch` to close after the first successful
download, or `--exit-after-fetch 30` to leave a 30-second grace period. Only the
generated mission endpoints and a plain-text map index are served; repository
files are not exposed.
