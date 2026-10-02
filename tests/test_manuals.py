# -*- coding: utf-8 -*-
"""Where a game's manual is found, ported from Kodi's own tests of the same rules."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources"))

from lib import manuals  # noqa: E402

GAME = "/games/Mega Drive/Sonic The Hedgehog 2 (World) (Rev A).md"


def disk(*files):
    """exists() and listdir() over a set of file paths."""
    files = set(files)

    def exists(path):
        return path in files

    def listdir(folder):
        return [f[len(folder):] for f in files if f.startswith(folder) and "/" not in f[len(folder):]]

    return exists, listdir


class Candidates(unittest.TestCase):
    def test_every_format_beside_the_game_comes_first(self):
        found = manuals.exact_candidates(GAME)
        self.assertEqual(found[:3], ["/games/Mega Drive/Sonic The Hedgehog 2 (World) (Rev A)" + e
                                     for e in (".pdf", ".cbz", ".cbr")])

    def test_the_manuals_subfolders_follow(self):
        found = manuals.exact_candidates(GAME)
        self.assertIn("/games/Mega Drive/manuals/Sonic The Hedgehog 2 (World) (Rev A).pdf", found)
        self.assertIn("/games/Mega Drive/Manuals/Sonic The Hedgehog 2 (World) (Rev A).pdf", found)

    def test_dots_inside_the_name_are_kept(self):
        self.assertEqual(manuals.exact_candidates("/g/Dr. Mario.nes")[0], "/g/Dr. Mario.pdf")

    def test_network_paths_work(self):
        self.assertEqual(manuals.exact_candidates("smb://box/games/Zelda.nes")[0], "smb://box/games/Zelda.pdf")

    def test_some_games_have_nowhere_for_a_manual(self):
        for path in ("", "/games/README", "zip://%2fgames%2fa.zip/game.nes", "plugin://x/y"):
            self.assertEqual(manuals.exact_candidates(path), [], path)


class Normalise(unittest.TestCase):
    def test_region_and_revision_tags_are_dropped(self):
        self.assertEqual(manuals.normalise("Sonic The Hedgehog 2 (World) (Rev A)"),
                         manuals.normalise("Sonic The Hedgehog 2"))
        self.assertEqual(manuals.normalise("Zelda (Europe) [!]"), manuals.normalise("Zelda"))

    def test_case_and_punctuation_are_ignored(self):
        self.assertEqual(manuals.normalise("Mega Man X2 - The Sequel!"),
                         manuals.normalise("mega man x2 the sequel"))

    def test_nested_tags_go_whole(self):
        self.assertEqual(manuals.normalise("Game (Unl (Aftermarket) More)"), "game")

    def test_different_games_stay_apart(self):
        self.assertNotEqual(manuals.normalise("Sonic The Hedgehog 2 (USA)"),
                            manuals.normalise("Sonic The Hedgehog 3 (USA)"))
        self.assertNotEqual(manuals.normalise("Sonic The Hedgehog (USA)"),
                            manuals.normalise("Sonic The Hedgehog 2 (USA)"))

    def test_an_empty_name_stays_empty(self):
        self.assertEqual(manuals.normalise(""), "")


class Find(unittest.TestCase):
    def test_a_manual_beside_the_game(self):
        manual = "/games/Mega Drive/Sonic The Hedgehog 2 (World) (Rev A).pdf"
        self.assertEqual(manuals.find(GAME, *disk(manual)), manual)

    def test_a_pdf_beats_a_comic_archive(self):
        base = "/games/Mega Drive/Sonic The Hedgehog 2 (World) (Rev A)"
        self.assertEqual(manuals.find(GAME, *disk(base + ".cbz", base + ".pdf")), base + ".pdf")

    def test_a_manual_in_either_subfolder(self):
        for sub in ("manuals", "Manuals"):
            manual = "/games/Mega Drive/%s/Sonic The Hedgehog 2 (World) (Rev A).cbz" % sub
            self.assertEqual(manuals.find(GAME, *disk(manual)), manual)

    def test_a_manual_tagged_differently(self):
        manual = "/games/Mega Drive/Manuals/Sonic The Hedgehog 2 (USA, Europe).pdf"
        self.assertEqual(manuals.find(GAME, *disk(manual)), manual)

    def test_an_exact_name_beats_a_tag_stripped_one(self):
        exact = "/games/Mega Drive/manuals/Sonic The Hedgehog 2 (World) (Rev A).pdf"
        other = "/games/Mega Drive/Sonic The Hedgehog 2 (Japan).pdf"
        self.assertEqual(manuals.find(GAME, *disk(other, exact)), exact)

    def test_another_games_manual_is_not_opened(self):
        self.assertEqual(manuals.find(GAME, *disk("/games/Mega Drive/Sonic The Hedgehog 3.pdf")), "")

    def test_nothing_when_there_is_no_manual(self):
        self.assertEqual(manuals.find(GAME, *disk()), "")


class DownloadTarget(unittest.TestCase):
    def test_the_manuals_folder_beside_the_game(self):
        self.assertEqual(manuals.download_target(GAME, set()),
                         "/games/Mega Drive/manuals/Sonic The Hedgehog 2 (World) (Rev A).pdf")

    def test_the_capitalised_folder_when_that_is_the_one_there(self):
        self.assertEqual(manuals.download_target(GAME, {"Manuals"}),
                         "/games/Mega Drive/Manuals/Sonic The Hedgehog 2 (World) (Rev A).pdf")

    def test_nowhere_for_a_game_without_a_folder(self):
        self.assertEqual(manuals.download_target("plugin://x/y", set()), "")


if __name__ == "__main__":
    unittest.main()
