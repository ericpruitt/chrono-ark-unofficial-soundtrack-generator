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
any operating systems that have the "ffmpeg" and "ffprobe" executables in a
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

**Track List:**

1. Chrono Ark Intro Theme
2. Title Screen Theme
3. Ark
4. Misty Garden 1 Field Theme
5. Misty Garden 1 Battle Theme
6. Misty Garden 1 Boss Theme
7. Chrono Ark Normal Theme
8. Mysterious Forest (Misty Garden 2 Field Theme)
9. Crush & Contort (Misty Garden 2 Battle Theme)
10. Hope for Existence (The Witch's Theme)
11. Shiranui Battle Theme
12. Encounter Dorchi
13. Place of Void (Bloody Park 1 Field Theme)
14. After Revive (Bloody Park 1 Battle Theme)
15. Bloody Park 1 Boss Theme
16. Show Time (The Joker's Theme)
17. The Phenomenon (Bloody Park 2 Field Theme)
18. Obstructor (Bloody Park 2 Battle Theme)
19. White Grave Field Theme
20. White Grave Battle Theme
21. Near the End (White Grave Boss Theme)
22. Sanctuary
23. Anxiety
24. End Of Light
25. Challenge (Early Access Azar Boss Theme)
26. Glitchy Chrono Ark Intro Theme
27. Chrono Ark Ex
28. Restart
29. Crimson Wilds
30. Crimson Wilds Battle Theme
31. Crimson Wilds Boss Theme
32. Azar Boss Theme Phase 1
33. Azar Boss Theme Phase 2
34. Program Master Boss Theme Phase 1
35. Program Master Boss Theme Phase 2
36. Memory Lane
37. Clock Tower Theme
38. Ark System
39. Infinity
40. Opposition
41. Dystopia
42. Ark Sight
43. Clone
44. Deeper, Deeper
45. Everything Meaning
46. It's Time to Choose
47. Outbreak
48. Abyss
49. Story Background Music
50. Story Serious Background Music
51. The Legendary Phoenix
52. There's No Way
53. Virtual Emotions
54. Wrong Beginning
55. End Credits Background Music
