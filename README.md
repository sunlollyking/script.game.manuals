# script.game.manuals

Shows the manual that came with a game, and finds one for a game that has none.

    RunScript(script.game.manuals, <game path>[, <manual path>])

A skin calls it from its game OSD or info screen; it also adds **Manual** to a
game's context menu.

## Where manuals are found

Beside the game, or in a `manuals` (or `Manuals`) folder next to it, named
like the game with `.pdf`, `.cbz` or `.cbr`. Names are also compared with their
bracketed tags removed, so `Sonic The Hedgehog 2 (World) (Rev A).md` finds
`Sonic The Hedgehog 2 (USA, Europe).pdf`.

PDFs are shown through [vfs.pdf](https://github.com/sunlollyking/vfs.pdf),
which this depends on; comic archives through Kodi's own zip and rar support.

## Finding one

A game with no manual opens a search. A manual provider is an ordinary plugin
that lists `manuals` among what it provides, and is called the way Kodi calls
a subtitle service:

    plugin://<provider>/?action=search&path=<game>&title=<name>

Each result's path is the manual, which is downloaded into the `manuals` folder
beside the game, or into this add-on's profile folder when that can't be
written to. [service.manuals.regvault](https://github.com/sunlollyking/service.manuals.regvault)
is one.

## Reading

| | Whole page | Zoomed in |
|---|---|---|
| Left / right | Turn the page | Move around it |
| Up / down | | Move around it |
| Triggers, mouse wheel | Zoom | Zoom |
| Select | Zoom in | Back to the whole page |
| Page up / down | Turn the page | Turn the page |

Each manual reopens at the page it was left on.

## Skins

The windows are `script-game-manuals-viewer.xml` and
`script-game-manuals-finder.xml`. A skin can provide its own; the viewer's page
is image control 100, which the add-on moves and resizes, and it publishes
`Window.Property(page)` and `Window.Property(zoomed)`.

## Tests

    python3 -m pytest tests
