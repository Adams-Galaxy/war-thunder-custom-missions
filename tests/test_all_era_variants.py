from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ERAS = {
    "1970-early": ("sam_site_s75", "sam_site_hawk_early"),
    "1970-late": ("sam_site_buk", "sam_site_hawk_1970"),
    "1980": ("sam_site_buk_m1", "sam_site_s300", "sam_site_hawk", "sam_site_patriot"),
}
MAPS = {
    "ne-archipelago-all-eras": (12, 6, 4),
    "ne-southeastern-city-all-eras": (10, 4, 4),
}
MODES = ("normal", "sead-training", "easy", "peaceful-exploration")


class AllEraVariantTests(unittest.TestCase):
    def mission(self, family: str, era: str, mode: str) -> str:
        return (ROOT / "missions" / family / era / f"{mode}.blk").read_text()

    def test_complete_matrix_is_generated_and_remote_sized(self) -> None:
        paths = [
            ROOT / "missions" / family / era / f"{mode}.blk"
            for family in MAPS
            for era in ERAS
            for mode in MODES
        ]
        self.assertEqual(len(paths), 24)
        for path in paths:
            with self.subTest(mission=path):
                self.assertTrue(path.is_file())
                self.assertLess(path.stat().st_size, 512 * 1024)
                text = path.read_text()
                self.assertEqual(text.count("{"), text.count("}"))
                self.assertNotIn("imports{", text)

    def test_era_specific_strategic_sites_are_retained(self) -> None:
        all_strategic = {name for names in ERAS.values() for name in names}
        for family in MAPS:
            for era, expected in ERAS.items():
                text = self.mission(family, era, "normal")
                with self.subTest(family=family, era=era):
                    for template in expected:
                        self.assertIn(f"{template}{{", text)
                    for template in all_strategic - set(expected):
                        self.assertNotIn(f"      {template}{{", text)

    def test_non_normal_modes_keep_sites_but_disable_channels(self) -> None:
        for family in MAPS:
            for era, templates in ERAS.items():
                normal = self.mission(family, era, "normal")
                self.assertNotIn("sam_site__missile_channels_max:i=0", normal)
                for mode in MODES[1:]:
                    text = self.mission(family, era, mode)
                    with self.subTest(family=family, era=era, mode=mode):
                        self.assertEqual(text.count("sam_site__missile_channels_max:i=0"), 16)
                        self.assertEqual(text.count("sam_site__target_channels_max:i=0"), 16)
                        for template in templates:
                            self.assertIn(f"{template}{{", text)

    def test_quick_start_package_is_only_on_enhanced_modes(self) -> None:
        for family, expected_spawns in MAPS.items():
            for era in ERAS:
                normal = self.mission(family, era, "normal")
                self.assertNotIn("_air_spawn{", normal)
                self.assertNotIn("afterRespawnDelaySec:i=30", normal)
                for mode in MODES[1:]:
                    text = self.mission(family, era, mode)
                    with self.subTest(family=family, era=era, mode=mode):
                        actual = (
                            text.count("_air_spawn{"),
                            text.count("_helicopter_spawn{"),
                            text.count("_naval_spawn{"),
                        )
                        self.assertEqual(actual, expected_spawns)
                        self.assertEqual(text.count("afterRespawnDelaySec:i=30"), 1)
                        self.assertEqual(
                            text.count("custom_gun_properties__attackMaxDist:r=12000.0"),
                            48,
                        )

    def test_easy_alone_gets_reduced_direct_defense_ranges(self) -> None:
        for family in MAPS:
            for era in ERAS:
                easy = self.mission(family, era, "easy")
                with self.subTest(family=family, era=era):
                    self.assertIn("threatSearchRad:r=4000.0", easy)
                    self.assertIn("threatSearchRad:r=8000.0", easy)
                for mode in ("normal", "sead-training", "peaceful-exploration"):
                    text = self.mission(family, era, mode)
                    self.assertNotIn("threatSearchRad:r=4000.0", text)
                    self.assertNotIn("threatSearchRad:r=8000.0", text)

    def test_peaceful_mode_protects_every_player(self) -> None:
        for family in MAPS:
            for era in ERAS:
                text = self.mission(family, era, "peaceful-exploration")
                with self.subTest(family=family, era=era):
                    self.assertIn('object:t="all_players_squad"', text)
                    self.assertIn("targetableByAi:b=no", text)
                    self.assertIn("isImmortal:b=yes", text)
                    self.assertIn("time:r=0.25", text)


if __name__ == "__main__":
    unittest.main()
