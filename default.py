# -*- coding: utf-8 -*-
"""RunScript(script.game.manuals, <game>[, <manual>])

Shows the game's manual, finding one first if the game has none.
"""

import sys

from resources.lib import main

main.run(sys.argv[1:])
