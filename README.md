Chrono Ark Unofficial Soundtrack Generator
==========================================

This repository contains a script to generate an unofficial soundtrack from the
Unity asset files of the rogue-like deckbuilder game [Chrono
Ark](https://store.steampowered.com/app/1188930/Chrono_Ark/). **This repository
does not include any copyrighted content from the Chrono Ark game and is
useless without the uncompressed game assets.** The script takes two arguments:
the first argument is the containing the audio assets, and the second is the
path to the output directory. If the output directory does not exist, it will
be created automatically as long as the parent directory exists. This script
depends on [FFmpeg](https://ffmpeg.org/) to generate the output files. Although
the script has only been tested on Linux with  Python 3.9+, it should work on
any operating system that have the "ffmpeg" and "ffprobe" executables in a
`$PATH`/`%PATH` directory and any version of Python starting from 3.6.

**NOTE:** I made this script because, at the time of this writing, the game's
music is not available for purchase. If you are reading this after the official
soundtrack has been released, please consider supporting the artists by
purchasing the music.

**Example:**

    $ ./make.py AudioClip "Chrono Ark Unofficial Soundtrack"
    Generating filter definitions...
    ...
    Done processing tracks.

    $ ls "Chrono Ark Unofficial Soundtrack/"
    01 - Chrono Ark Intro Theme.flac
    02 - Title Screen Theme.flac
    03 - Ark.flac
    04 - Misty Garden 1 Field Theme.flac
    05 - Misty Garden 1 Battle Theme.flac
    06 - Misty Garden 1 Boss Theme.flac
    07 - Chrono Ark Normal Theme.flac
    08 - Mysterious Forest (Misty Garden 2 Field Theme).flac
    09 - Crush & Contort (Misty Garden 2 Battle Theme).flac
    ...
