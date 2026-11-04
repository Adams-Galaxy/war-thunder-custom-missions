import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MISSION = REPO_ROOT / "missions/poland-nimitz-lake/poland-nimitz-lake.blk"


class PolandForrestalLakeTests(unittest.TestCase):
    def test_generated_custom_room_keeps_its_required_map_and_carrier(self):
        text = MISSION.read_text(encoding="utf-8")
        self.assertIn('type:t="domination"', text)
        self.assertIn('level:t="levels/avg_poland.bin"', text)
        self.assertEqual(text.count('unit_class:t="us_aircraftcarrier_forrestal_ai"'), 1)
        self.assertIn('target:t="us_forrestal_lake"', text)
        # These are the exact player-wing counts from the live Poland TDM
        # source, rather than guesses made by a hand-authored mission shell.
        self.assertEqual(text.count('wing:t="t1_player'), 16)
        self.assertEqual(text.count('wing:t="t2_player'), 17)
        self.assertEqual(text.count("{"), text.count("}"))


if __name__ == "__main__":
    unittest.main()
