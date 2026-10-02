# -*- coding: utf-8 -*-
"""The manual itself, a page at a time.

While a page is shown whole the arrows turn pages; zoomed in they move around
it, as Kodi's picture viewer does. The shoulder buttons turn pages too, Select
toggles between the whole page and a close look, and the manual reopens where
it was left.
"""

import xbmcgui
import xbmcvfs

from . import pages, view
from .main import localize

PAGE = 100
#: The area a page is shown in when the skin gives control 100 no size
AREA = (1920, 1080)
#: Enough of a picture to reach its size, past a JPEG's metadata
HEADER_BYTES = 65536

LEFT, RIGHT, UP, DOWN = 1, 2, 3, 4
PAGE_UP, PAGE_DOWN, NEXT_ITEM, PREV_ITEM = 5, 6, 14, 15
SELECT, PREVIOUS_MENU, NAV_BACK = 7, 10, 92
SHOW_GUI, QUEUE_ITEM, ZOOM_NORMAL = 18, 34, 37
ZOOM_OUT, ZOOM_IN = 30, 31
WHEEL_UP, WHEEL_DOWN, SCROLL_UP, SCROLL_DOWN = 104, 105, 111, 112


def picture_size(path):
    f = xbmcvfs.File(path)
    try:
        return pages.picture_size(bytes(f.readBytes(HEADER_BYTES)))
    finally:
        f.close()


class Viewer(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        super(Viewer, self).__init__(*args)
        self.manual = kwargs["manual"]
        self.title = kwargs.get("title", "")
        self.paths = kwargs["pages"]
        self.positions = kwargs["positions"]
        self.index = min(self.positions.page(self.manual), len(self.paths) - 1)
        self.view = None
        self.image = None
        self.origin = (0, 0)

    def onInit(self):
        self.setProperty("title", self.title)
        self.image = self.getControl(PAGE)
        # Where the skin puts control 100 is the area the page is fitted to,
        # which leaves a skin room for anything it shows around the page
        area = (self.image.getWidth(), self.image.getHeight())
        if min(area) > 0:
            self.origin = (self.image.getX(), self.image.getY())
        else:
            area = AREA
        self.view = view.View(*area)
        self.show_page()

    def show_page(self):
        path = self.paths[self.index]
        self.view.show(*(picture_size(path) or self.view.area))
        self.image.setImage(path)
        self.place()
        self.setProperty("page", localize(32001).format(self.index + 1, len(self.paths)))

    def place(self):
        x, y, width, height = self.view.rect()
        self.image.setPosition(self.origin[0] + x, self.origin[1] + y)
        self.image.setWidth(width)
        self.image.setHeight(height)
        self.setProperty("zoomed", "" if self.view.is_whole else "true")

    def turn(self, pages_on):
        index = min(max(self.index + pages_on, 0), len(self.paths) - 1)
        if index != self.index:
            self.index = index
            self.show_page()

    def onAction(self, action):
        action_id = action.getId()
        moved = False
        if action_id in (PREVIOUS_MENU, NAV_BACK):
            self.positions.remember(self.manual, self.index)
            self.close()
        elif action_id in (LEFT, RIGHT):
            step = -1 if action_id == LEFT else 1
            if self.view.is_whole:
                self.turn(step)
            else:
                moved = self.view.pan(step, 0)
        elif action_id in (UP, DOWN):
            moved = self.view.pan(0, -1 if action_id == UP else 1)
        elif action_id in (PAGE_UP, PREV_ITEM, SCROLL_UP):
            self.turn(-1)
        elif action_id in (PAGE_DOWN, NEXT_ITEM, SCROLL_DOWN):
            # Kodi's gamepad keymap sends Scroll from the bumpers and the
            # triggers alike, so both turn pages
            self.turn(1)
        elif action_id in (ZOOM_IN, WHEEL_UP):
            moved = self.view.step(1)
        elif action_id in (ZOOM_OUT, WHEEL_DOWN):
            moved = self.view.step(-1)
        elif action_id == SELECT:
            moved = self.view.whole() if not self.view.is_whole else self.view.step(2)
        elif action_id in (SHOW_GUI, QUEUE_ITEM, ZOOM_NORMAL):
            moved = self.view.whole()
        if moved:
            self.place()
