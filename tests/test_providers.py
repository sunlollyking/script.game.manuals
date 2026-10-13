# -*- coding: utf-8 -*-
"""Recognising a manual provider, and asking one."""

import os
import sys
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources"))

from lib import providers  # noqa: E402

REGVAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                        "plugin.game.manuals.regvault", "addon.xml")


class IsProvider(unittest.TestCase):
    def test_a_provider_is_known_by_its_id(self):
        self.assertTrue(providers.is_provider("plugin.game.manuals.regvault"))

    def test_other_plugins_are_not_providers(self):
        self.assertFalse(providers.is_provider("plugin.program.iagl"))
        self.assertFalse(providers.is_provider("plugin.game.manuals"))

    def test_regvault_is_one(self):
        if not os.path.exists(REGVAULT):
            self.skipTest("plugin.game.manuals.regvault is not checked out beside this")
        root = ET.parse(REGVAULT).getroot()
        self.assertTrue(providers.is_provider(root.get("id")))


class SearchUrl(unittest.TestCase):
    def test_the_path_and_title_are_handed_over(self):
        url = providers.search_url("plugin.game.manuals.regvault", "/games/Super Mario Bros. (USA, Europe).nes")
        parts = urlsplit(url)
        self.assertEqual((parts.scheme, parts.netloc), ("plugin", "plugin.game.manuals.regvault"))
        self.assertEqual(parse_qs(parts.query), {"action": ["search"],
                                                 "path": ["/games/Super Mario Bros. (USA, Europe).nes"],
                                                 "title": ["Super Mario Bros."]})

    def test_a_title_given_is_the_hint(self):
        url = providers.search_url("p", "/g/smb.nes", "Super Mario Bros.")
        self.assertEqual(parse_qs(urlsplit(url).query)["title"], ["Super Mario Bros."])


if __name__ == "__main__":
    unittest.main()
