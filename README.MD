# Quester

A quest-tracking sim: complete quests to level up, unlock a 2D platform world,
and place blocks with the levels you earn. A random villager moves in every 10 levels.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Controls

- **Type a quest** in the box, then press Enter or click **Add**.
- **Done** completes a quest (permanent); **X** deletes an open one.
- **Arrow keys** scroll the world left/right.
- **1–5** or the toolbar buttons pick a block; **Break** removes one.
- **Click** a tile to place/break, or **click a villager** to hear a line.
- Progress saves automatically to `save.json` next to the program.

## Building a Windows .exe

PyInstaller bundles the script and a Python interpreter into one executable.
It does **not** cross-compile — run this on Windows to get a `.exe`, on macOS/Linux
you'll get a native binary for that OS instead.

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Quester main.py
```

The result is `dist/Quester.exe`. `save.json` will be created next to that file
the first time it runs. If you ever want the exe built automatically on every
push (via GitHub Actions, so you don't need a Windows machine), just ask.

## Project layout

- `main.py` — game loop, UI, rendering
- `quests.py` — quest log and leveling
- `world.py` — world generation and tile rules
- `npc.py` — villager behavior and dialogue
- `storage.py` — save/load (`save.json`)