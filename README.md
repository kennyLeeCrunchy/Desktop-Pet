# Desktop Pet

## KIMACHI Desktop Pet

![Kimachi preview](docs/kimachi-preview.png)

KIMACHI is a fan-made animated desktop pet based on
[Kim Chaewon's](https://le-sserafim.fandom.com/wiki/Kim_Chaewon)
representative character. She is a brave, focused, and slightly tsundere
golden baby cheetah who can live in Codex or directly on a Windows desktop.

## Galgyo Desktop Pet

![Galgyo preview](docs/galgyo-preview.png)

Galgyo is a fan-made animated desktop pet based on a derivative character
inspired by aespa member [Winter](https://en.wikipedia.org/wiki/Winter_(singer)).
This cute white puppy can live in Codex or directly on a Windows desktop.
Galgyo is an unofficial, non-commercial fan-made derivative character; this
project is not affiliated with or endorsed by aespa, Winter, SM Entertainment,
or any rights holder. Character and related IP rights remain with the original
creators and applicable rights holders.

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

### Galgyo Windows desktop app

Download [GALGYO-Windows.zip](publish/GALGYO-Windows.zip), extract it, and
double-click `GALGYO.exe`. Codex and Python are not required.

### Galgyo Codex and Petdex package

Download [galgyo-petdex.zip](publish/galgyo-petdex.zip). The package contains
the Codex-compatible `pet.json` and v2 `spritesheet.webp`.

To install it manually in Codex, extract the `galgyo` folder into:

```text
~/.codex/pets/galgyo
```

Then open Codex and select Galgyo under **Settings → Appearance → Pets**.

Galgyo is an unofficial, non-commercial derivative character inspired by
aespa member Winter. This project is not affiliated with or endorsed by aespa,
Winter, SM Entertainment, or any rights holder. Character and related IP
rights remain with the original creators and applicable rights holders.

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
desktop-pet/              KIMACHI Windows app source and build script
desktop-pet-galgyo/       Galgyo Windows app source and build script
publish/KIMACHI-App/      Unpacked Windows release
publish/KIMACHI-Windows.zip
publish/kimachi/          Codex-compatible pet package
publish/kimachi-petdex.zip
publish/galgyo-app/       Unpacked Galgyo Windows release
publish/GALGYO-Windows.zip
publish/galgyo/            Codex-compatible Galgyo pet package
publish/galgyo-petdex.zip
```

## Build the Windows apps

Install Python with Tkinter, Pillow, and PyInstaller, then run:

```powershell
.\desktop-pet\build.ps1
.\desktop-pet-galgyo\build.ps1
```

The builds are written to `publish/KIMACHI-App` and `publish/galgyo-app`.

## Disclaimer

This is an unofficial fan-made project and is not affiliated with or endorsed
by Kim Chaewon, LE SSERAFIM, Source Music, or HYBE. Character and related rights
belong to their respective owners.
