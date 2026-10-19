import unittest
from unittest.mock import patch

from tools.dynamic_missions import public_dns_addresses


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class PublicDnsTests(unittest.TestCase):
    @patch("tools.dynamic_missions.urlopen")
    def test_extracts_public_address(self, mocked_open) -> None:
        response = FakeResponse()
        response.read = lambda: b'{"Status":0,"Answer":[{"name":"x","type":1,"data":"203.0.113.2"}]}'
        mocked_open.return_value = response
        self.assertEqual(public_dns_addresses("example.test"), ["203.0.113.2"])

    @patch("tools.dynamic_missions.urlopen", side_effect=OSError("offline"))
    def test_dns_failure_is_not_ready(self, mocked_open) -> None:
        self.assertEqual(public_dns_addresses("example.test"), [])


if __name__ == "__main__":
    unittest.main()
