from pathlib import Path
import tempfile
import unittest

from tools.dynamic_missions import build_all, deep_merge, load_profiles


ROOT = Path(__file__).resolve().parents[1]


class DynamicMissionTests(unittest.TestCase):
    def test_deep_merge_preserves_siblings(self) -> None:
        base = {"defenses": {"strategic_sams": "silent", "range": 18}}
        override = {"defenses": {"strategic_sams": "stock"}}
        self.assertEqual(
            deep_merge(base, override),
            {"defenses": {"strategic_sams": "stock", "range": 18}},
        )

    def test_profiles_demonstrate_map_override(self) -> None:
        profiles = load_profiles(ROOT / "config")
        self.assertEqual(
            profiles["archipelago-2018"]["defenses"]["strategic_sams"],
            "silent",
        )
        self.assertEqual(
            profiles["south-eastern-city"]["defenses"]["strategic_sams"],
            "stock",
        )

    def test_builds_every_configured_map(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            built = build_all(ROOT / "config", Path(directory))
        self.assertEqual(set(built), {"archipelago-2018", "south-eastern-city"})

        archipelago = built["archipelago-2018"].decode()
        self.assertIn("sam_site__missile_channels_max:i=0", archipelago)
        self.assertIn("isHelicoptersAllowed:b=yes", archipelago)
        self.assertIn("isShipsAllowed:b=yes", archipelago)
        self.assertIn("isTanksAllowed:b=no", archipelago)
        self.assertEqual(archipelago.count("_helicopter_spawn{"), 6)
        self.assertEqual(archipelago.count("_naval_spawn{"), 4)

        city = built["south-eastern-city"].decode()
        self.assertNotIn("sam_site__missile_channels_max:i=0", city)
        self.assertIn('level:t="levels/air_south_eastern_city.bin"', city)
        self.assertIn("isTanksAllowed:b=no", city)


if __name__ == "__main__":
    unittest.main()
