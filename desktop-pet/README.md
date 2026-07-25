# KIMACHI Desktop Pet

A standalone Windows desktop pet based on Kimachi, Kim Chaewon's representative character. Codex is not required.

## Controls

- Left-drag KIMACHI to move her around the desktop. Dragging left or right
  automatically plays the matching directional running animation.
- Double-click Kimachi to make her wave.
- Right-click Kimachi to open the action menu.
- Choose a visible action such as Blinking, Waving, Jumping, Feeling Sad,
  Asking, Thinking, or Sitting.
- Use **Hover Action** to choose the animation played while the pointer is
  over KIMACHI, or disable hover behavior.
- Use **Resize...** for continuous scaling from 50% to 200%.
- Use **Always on Top** and **Lock Position** for display preferences.
- Choose **Quit** from the right-click menu to close the pet.

Settings are stored in `%APPDATA%\KimachiDesktopPet\settings.json`.

## Build

Run `build.ps1` from PowerShell with Python, PyInstaller, Pillow, and Tkinter available.
