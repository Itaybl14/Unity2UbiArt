# Just Dance Unity2UbiArt Converter
A simple script for converting Unity Just Dance tape's to UbiArt Just Dance tape's for making them playable in older Just Dance games (2016-2022).

## Authors
- [Itay](https://github.com/Itaybl14)
- [Rama](https://github.com/rama0dev)
- [Worte](https://github.com/wortestudios)

## Input Options
- **mapPackage**: Unity AssetBundles (`.bundle`) from JD+ files
- **Raw Input**: Check [input examples](./input/MapName) for more details
- **SongDB**: Database containing song information

## Requirements
### Installation
To install UnityPy properly, use the following command:
```bash
pip install unitypy==1.10.6
```
### Audio Cutter
You'll also need to install FFmpeg. Make sure the FFmpeg executable is located in the ./bin directory. You can disable this in the `config.json` file if preferred.

## Credits
- **nvcompress**: [castano/nvidia-texture-tools](https://github.com/castano/nvidia-texture-tools)

### License
Please remember to credit the authors if you use or modify this script in your work.

![WatchOutForThis](https://ramastuff.ramaprojects.ru/other/Unity2UbiArt.png)