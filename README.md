# Pixel Jump Adventure

Original 2D platform game written in Python. No copyrighted Mario assets.

## Run on a computer

Install Python 3.11+ and then:

```bash
python -m pip install -r requirements.txt
python main.py
```

## Publish for browser play (GitHub Pages)

Pygbag can build a web version of this pygame-ce game.

```bash
python -m pip install pygbag
python -m pygbag --build main.py
```

Pygbag CLI may expect the directory containing main.py rather than a file, depending on version. If so, run `python -m pygbag --build .` from this folder. Upload the resulting web build files (usually in build/web) to a GitHub Pages publishing branch or folder. GitHub Pages cannot execute Python server-side; Pygbag converts the game for browser use. Test the build locally before publishing.

## Controls

Arrow keys or A/D to move, Space/W/Up to jump. Touch buttons for mobile. Press Enter to start or restart. Collect coins, jump on enemies, reach the yellow flag. Three levels and three lives.

Note: browser touch behavior can vary by device. For a polished mobile release, further touch and viewport testing is recommended.
