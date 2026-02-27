# Just Dance Unity2UbiArt Converter

A simple script for converting Unity Just Dance tape's to UbiArt Just Dance tape's, making them playable in older Just Dance games (2016–2022).

---

## Input Options

* **mapPackage**: Unity AssetBundles (`.bundle`) from JD+ files
* **Raw Input**: Check [input examples](./input/MapName) for more details
* **SongDB**: Database containing song information

---

## Requirements

### AssetStudioModCLI (Required)

Download **AssetStudioModCLI** from:

👉 [https://github.com/aelurum/AssetStudio/releases](https://github.com/aelurum/AssetStudio/releases)

After downloading, place `AssetStudioModCLI.exe` inside:

```
./bin/AssetStudioModCLI/
```

The script will not work if the CLI is placed elsewhere.

---

### Audio Cutter (Optional)

You'll also need to install **FFmpeg**.

Download FFmpeg from:

👉 [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

Place the `ffmpeg.exe` inside:

```
./bin/
```

You can disable audio cutting in `config.json` if preferred.

---

## License

Please remember to credit the authors if you use or modify this script in your work.

---

![WatchOutForThis](https://ramastuff.ramaprojects.ru/other/Unity2UbiArt.png)

---
