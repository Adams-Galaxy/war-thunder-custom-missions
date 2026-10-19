import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class MaintainedVariantTests(unittest.TestCase):
    def test_non_normal_variants_have_quick_start_package(self) -> None:
        cases = {
            "missions/ne-archipelago-2018/sead-training-hq11-18km.blk": (12, 6, 4),
            "missions/ne-archipelago-2018/no-lrsam.blk": (12, 6, 4),
            "missions/ne-southeastern-city/sead-training-hq11-18km.blk": (10, 4, 4),
            "missions/ne-southeastern-city/no-long-range-sams.blk": (10, 4, 4),
        }

        for relative_path, expected_spawns in cases.items():
            with self.subTest(mission=relative_path):
                text = (REPO_ROOT / relative_path).read_text()
                actual_spawns = (
                    text.count("_air_spawn{"),
                    text.count("_helicopter_spawn{"),
                    text.count("_naval_spawn{"),
                )
                self.assertEqual(actual_spawns, expected_spawns)
                self.assertEqual(
                    text.count(
                        "custom_gun_properties__attackMaxDist:r=18000.0"
                    ),
                    48,
                )
                self.assertEqual(text.count("afterRespawnDelaySec:i=30"), 1)
                self.assertEqual(text.count("isHelicoptersAllowed:b=yes"), 1)
                self.assertEqual(text.count("isShipsAllowed:b=yes"), 1)
                self.assertEqual(text.count("isTanksAllowed:b=no"), 1)
                self.assertEqual(text.count("{"), text.count("}"))

    def test_normal_variants_do_not_receive_quick_start_package(self) -> None:
        for relative_path in (
            "missions/ne-archipelago-2018/source.blk",
            "missions/ne-southeastern-city/normal.blk",
        ):
            with self.subTest(mission=relative_path):
                text = (REPO_ROOT / relative_path).read_text()
                self.assertNotIn("_air_spawn{", text)
                self.assertNotIn("_helicopter_spawn{", text)
                self.assertNotIn("_naval_spawn{", text)
                self.assertNotIn(
                    "custom_gun_properties__attackMaxDist:r=18000.0", text
                )


if __name__ == "__main__":
    unittest.main()
