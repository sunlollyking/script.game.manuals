# -*- coding: utf-8 -*-
"""Finding a manual for a game that has none.

Each installed provider is asked in the background; picking a result fetches
it into the manuals folder beside the game, or into the profile when that
folder can't be written to, and the viewer then opens it.
"""

import threading

import xbmc
import xbmcgui
import xbmcvfs

from . import manuals, providers
from .main import PROFILE_MANUALS, jsonrpc, localize, log

RESULTS = 200
PROVIDER = 300
MORE = 310
CHUNK = 256 * 1024


def find_providers():
    """The installed add-ons that find manuals, as (id, name, icon)."""
    found = []
    answer = jsonrpc("Addons.GetAddons", {"type": "xbmc.python.pluginsource", "enabled": True,
                                          "properties": ["name", "path", "thumbnail"]})
    for addon in answer.get("addons") or []:
        manifest = manuals.join(addon.get("path") or "", "addon.xml")
        try:
            with xbmcvfs.File(manifest) as f:
                text = f.read()
        except Exception:
            continue
        if providers.provides_manuals(text):
            found.append((addon["addonid"], addon.get("name") or addon["addonid"], addon.get("thumbnail") or ""))
    return found


class Finder(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        super(Finder, self).__init__(*args)
        self.game = kwargs["game"]
        self.downloaded = ""
        self.providers = []
        self.provider = 0
        self.busy = False

    def onInit(self):
        self.setProperty("game", manuals.stem_of(self.game))
        self.providers = find_providers()
        if not self.providers:
            self.setProperty("status", localize(32005))
            self.setFocusId(MORE)
            return
        self.search()

    def search(self):
        addon_id, name, _ = self.providers[self.provider]
        self.setProperty("provider", name)
        self.setProperty("status", localize(32003))
        self.getControl(RESULTS).reset()
        threading.Thread(target=self._search, args=(addon_id,)).start()

    def _search(self, addon_id):
        answer = jsonrpc("Files.GetDirectory", {"directory": providers.search_url(addon_id, self.game),
                                                "media": "files", "properties": ["title", "art"]})
        items = []
        for result in answer.get("files") or []:
            item = xbmcgui.ListItem(result.get("label") or result.get("title") or "")
            item.setProperty("url", result.get("file") or "")
            item.setArt(result.get("art") or {})
            items.append(item)
        results = self.getControl(RESULTS)
        results.addItems(items)
        if items:
            self.setProperty("status", "")
            self.setFocusId(RESULTS)
        else:
            self.setProperty("status", localize(32004))
            self.setFocusId(PROVIDER if len(self.providers) > 1 else MORE)

    def onClick(self, control_id):
        if self.busy:
            return
        if control_id == RESULTS:
            item = self.getControl(RESULTS).getSelectedItem()
            if item and item.getProperty("url"):
                self.download(item.getProperty("url"))
        elif control_id == PROVIDER and len(self.providers) > 1:
            self.provider = (self.provider + 1) % len(self.providers)
            self.search()
        elif control_id == MORE:
            self.close()
            xbmc.executebuiltin("ActivateWindow(addonbrowser,addons://search/manuals/,return)")

    def target(self):
        """Beside the game if that can be written to, otherwise in the profile."""
        folder = manuals.folder_of(self.game)
        existing = set(xbmcvfs.listdir(folder)[0]) if xbmcvfs.exists(folder) else set()
        beside = manuals.download_target(self.game, existing)
        if beside:
            folder = manuals.folder_of(beside)
            if xbmcvfs.exists(folder) or xbmcvfs.mkdirs(folder):
                return beside
            log("\"%s\" can't be written to; keeping the manual in the profile" % folder)
        xbmcvfs.mkdirs(PROFILE_MANUALS)
        return manuals.join(PROFILE_MANUALS, manuals.stem_of(self.game) + ".pdf")

    def download(self, url):
        self.busy = True
        target = self.target()
        progress = xbmcgui.DialogProgressBG()
        progress.create(localize(32000), localize(32007))
        partial = target + ".part"
        done = False
        try:
            source = xbmcvfs.File(url)
            size = source.size()
            copied = 0
            with xbmcvfs.File(partial, "w") as out:
                while True:
                    data = source.readBytes(CHUNK)
                    if not data:
                        break
                    out.write(data)
                    copied += len(data)
                    if size > 0:
                        progress.update(int(copied * 100 / size))
            source.close()
            done = copied > 0 and (size <= 0 or copied == size) and xbmcvfs.rename(partial, target)
        except Exception as error:
            log("Fetching the manual failed: %s" % error, xbmc.LOGERROR)
        finally:
            progress.close()
            self.busy = False
        if not done:
            xbmcvfs.delete(partial)
            self.setProperty("status", localize(32008))
            return
        log("Fetched a manual to \"%s\"" % target)
        self.downloaded = target
        self.close()
