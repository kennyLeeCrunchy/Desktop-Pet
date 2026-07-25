# KIMACHI Desktop Pet

![Kimachi preview](docs/kimachi-preview.png)

KIMACHI is a fan-made animated desktop pet based on
[Kim Chaewon's](https://le-sserafim.fandom.com/wiki/Kim_Chaewon)
representative character. She is a brave, focused, and slightly tsundere
golden baby cheetah who can live in Codex or directly on a Windows desktop.

## Download

### Windows desktop app

Download [KIMACHI-Windows.zip](publish/KIMACHI-Windows.zip), extract it, and
double-click `KIMACHI.exe`. Codex and Python are not required.

Windows may show a SmartScreen warning because this personal build is not
code-signed. Only run files downloaded from a source you trust.

### Codex and Petdex package

Download [kimachi-petdex.zip](publish/kimachi-petdex.zip). The package contains
the Codex-compatible `pet.json` and v2 `spritesheet.webp`.

To install it manually in Codex, extract the `kimachi` folder into:

```text
~/.codex/pets/kimachi
```

Then open Codex and select Kimachi under **Settings → Appearance → Pets**.

## Windows controls

- Left-drag KIMACHI to move her; the drag direction selects the matching
  animation.
- Double-click her to wave.
- Right-click her to choose an action or change settings.
- Use **Hover Action** to decide what she does when the pointer is over her.
- Use **Resize...** for continuous scaling from 50% to 200%.
- Use **Always on Top** and **Lock Position** for display preferences.
- Choose **Quit** from the right-click menu to close the app.

Settings are stored in:

```text
%APPDATA%\KimachiDesktopPet\settings.json
```

## Repository layout

```text
desktop-pet/              Windows app source and build script
publish/KIMACHI-App/      Unpacked Windows release
publish/KIMACHI-Windows.zip
publish/kimachi/          Codex-compatible pet package
publish/kimachi-petdex.zip
```

## Build the Windows app

Install Python with Tkinter, Pillow, and PyInstaller, then run:

```powershell
.\desktop-pet\build.ps1
```

The build is written to `publish/KIMACHI-App`.

## Disclaimer

This is an unofficial fan-made project and is not affiliated with or endorsed
by Kim Chaewon, LE SSERAFIM, Source Music, or HYBE. Character and related rights
belong to their respective owners.
