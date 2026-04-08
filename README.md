

# snip2path

A lightweight snipping tool that supercharges your CLI-based development workflow (Claude Code, etc.).

[日本語版はこちら](README.ja.md)

## Problem

- Referencing Windows clipboard images from Docker/WSL environments is painful.
- Sharing a screenshot requires "save → copy path → paste it" — breaking your flow every time.

## Core Philosophy

- **"One image is enough"** — Always overwrites `latest.png`. No history, no clutter.
- **"Automate path management"** — Automatically creates a `.snips/` folder per project.
- **"Keep the visual in view"** — Floats the snipped image on your desktop after capture.

## Features

1. **Project linking**
   - Creates a `.snips/` folder inside your repository.
   - Hard-links `.snips/latest.png` to the central `~/.snip2path/latest.png`.

2. **Snip & overwrite**
   - Select a region on screen.
   - Always overwrites `./.snips/latest.png` — no versioning needed.

3. **Clipboard integration**
   - Copies the relative path `./.snips/latest.png` to the clipboard immediately after capture.

4. **Floating preview**
   - Displays the captured image as a floating window.
   - Not pinned to front — place it wherever works for you.
   - Automatically closes on the next snip.

5. **Capture delay**
   - Optional 3 / 5 / 7 second delay before capture, so you can set up the screen first.

## Tech Stack

- Python 3.10+
- PySide6 (GUI / Overlay / Window management)
- Pillow (Image capture & processing)
- pyperclip (Clipboard)

## Build (Windows)

```bat
build.bat
```

Produces `dist\snip2path\snip2path.exe`.

## Requirements

- Windows 10 / 11
- Python 3.10+ (for building from source)


![Animation](https://github.com/user-attachments/assets/ea15b9fd-fbf7-412d-86c3-da0606c1620f)
