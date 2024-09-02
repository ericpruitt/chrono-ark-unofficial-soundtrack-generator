#!/usr/bin/env python3
"""
Usage: ./make.py AUDIO_ASSETS_DIRECTORY OUTPUT_DIRECTORY

Generate an unofficial soundtrack from the Unity asset files of the rogue-like
deckbuilder game Chrono Ark.
"""
import functools
import os
import shlex
import subprocess
import sys

# Users used to running commands inside a shell on Windows may expect commands
# in the same directory as the script to be implicitly be examined before
# %PATH% folders.
if sys.platform == "win32":
    if os.environ.get("PATH"):
        os.environ["PATH"] = os.getcwd() + ";" + os.environ["PATH"]
    else:
        os.environ["PATH"] = os.getcwd()


@functools.lru_cache
def track_length(path):
    """
    Get the length of an audio file.

    Arguments:
    - path: Path to the file.

    Return: The length of the file in seconds.
    """
    output = subprocess.check_output([
        "ffprobe",
        "-i", path,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "csv=p=0"
    ])

    return float(output)


def fade_in(source, duration):
    """
    Apply a fade in effect to the specified audio source.

    Arguments:
    - source: Audio source. This can be a file name or a file name that has
      been processed by "fade_in" or "volume".
    - duration: Number of seconds the fade in should take.

    Return: Metadata used by "build_track" function to generate the output
    file.
    """
    return f"afade=type=in:start_time=0:duration={duration}\0" + source


def fade_out(source, start, duration=None):
    """
    Apply a fade out effect to the specified audio source.

    Arguments:
    - source: Audio source. This can be a file name or a file name that has
      been processed by "fade_in" or "volume".
    - start: Offset in the source audio where the fade begins. If this is
      negative, it is interpreted as the number of seconds from the end of the
      file.
    - duration: Number of seconds the fade out should take. If this is omitted,
      the fade out spans the remainder of the track.

    Return: Metadata used by "build_track" function to generate the output
    file.
    """
    if start < 0:
        if duration is None:
            duration = -start

        eof = track_length(source.split("\0")[-1])
        start = eof + start
    elif duration is None:
        eof = track_length(source.split("\0")[-1])
        duration = eof - start

    return (
        f"afade=type=out:start_time={start}:duration={duration}\0" +
        f"atrim=start=0:end={start + duration}\0" +
        source
    )


def volume(source, value):
    """
    Adjust the volume to the specified audio source.

    Arguments:
    - source: Audio source. This can be a file name or a file name that has
      been processed by "fade_in" or "fade_out".
    - value: The volume value. This can be a number or a string to, for
      example, specify a decibel adjustment. See
      <https://trac.ffmpeg.org/wiki/AudioVolume> for details.

    Return: Metadata used by "build_track" function to generate the output
    file.
    """
    return (
        f"volume={value}\0" +
        source
    )


def build_track(output_directory, track, trackno):
    """
    Build a track based on the specified metadata.

    Arguments:
    - track: Track metadata.
    - trackno: Track number within the album.
    """
    basename = f'{trackno:02d} - {track["name"]}.flac'
    output = os.path.join(output_directory, basename)

    if os.path.exists(output):
        return

    argv = ["ffmpeg", "-v", "quiet"]
    components = []
    filter_graph = []
    filter_id = 0

    gap = track.get("gap", 0)
    assert gap >= 0

    lyrics_file = track.get("lyrics-file")

    for file_index, source in enumerate(track["parts"]):
        parts = source.split("\0")
        path = parts[-1]
        filters = parts[:-1]
        argv += ["-i", path]

        if filters:
            # Chain the input through all defined filters and use the final
            # output stream ID as the "concat" stream argument.
            for filter_index, desc in enumerate(filters):
                stream_in = (
                    f"[f{filter_id}]" if filter_index else f"[{file_index}]"
                )
                filter_id += 1
                filter_graph.append(f"{stream_in} {desc} [f{filter_id}]")

            components.append(f"[f{filter_id}]")
        else:
            components.append(f"[{file_index}]")

    if gap:
        components.append("[silence]")
        filter_graph.append(
            f"anullsrc=r=48000:duration={gap} [silence]"
        )

    filter_graph.append(
        f"{''.join(components)} concat=n={len(components)}:v=0:a=1 [out]"
    )

    argv += [
        "-filter_complex", "; ".join(filter_graph),
        "-map", "[out]",
        "-metadata", "DATE=2024",
        "-metadata", f"TITLE={track['name']}",
        "-metadata", f"TRACKNUMBER={trackno}",
    ]

    if track.get("artist"):
        argv += ["-metadata", f"ARTIST={track['artist']}"]

    if lyrics_file:
        with open(os.path.join(os.path.dirname(__file__), lyrics_file),
          encoding="utf8") as fd:
            argv += ["-metadata", f"LYRICS={fd.read()}"]

    argv += [output]

    print(f"{basename}:", *map(shlex.quote, argv))
    subprocess.check_call(argv)


def main(argv):
    arguments = argv[1:]

    if len(arguments) != 2:
        command = os.path.basename(argv[0])
        print(f"Usage: ./{command} AUDIO_ASSETS_DIRECTORY OUTPUT_DIRECTORY",
            file=sys.stderr)
        return 1

    assets_directory, output_directory = arguments

    try:
        os.mkdir(output_directory)
    except FileExistsError:
        pass

    output_directory = os.path.abspath(output_directory)
    os.chdir(assets_directory)

    print("Generating filter definitions...")

    # Where possible, track names were copied from
    # <https://selector.bandcamp.com/album/chrono-ark-ost> and
    # <https://soundcloud.com/cosmogrph/sets/chrono-ark-work>.
    tracks = [
        {
            "name": "Chrono Ark Intro Theme",
            "parts": [
                "choronoArk_intro.wav",
            ],
        },

        {
            "name": "Title Screen Theme",
            "parts": [
                "Main.wav",
            ],
        },

        {
            "name": "Ark",
            "artist": "Cosmograph",
            "parts": [
                "bangjoo_intro.wav",
                fade_out("bangjoo_loop.wav", 40, 6.5),
            ],
        },

        {
            "name": "Misty Garden 1 Field Theme",
            "parts": [
                "CA_Field01_2.wav",
                fade_out("CA_Field01_2.wav", 56, 8),
            ],
            "gap": 1,
        },

        {
            "name": "Misty Garden 1 Battle Theme",
            "parts": [
                "CA_Battle01.wav",
                fade_out("CA_Battle01.wav", 60, 5),
            ],
            "gap": 1,
        },

        {
            "name": "Misty Garden 1 Boss Theme",
            "parts": [
                fade_out("CA_Boss01.wav", 113, 10),
            ],
            "gap": 1,
        },

        {
            "name": "Chrono Ark Normal Theme",
            "parts": [
                "chronoArk_normal.wav",
                fade_out("chronoArk_normal.wav", 55, 5),
            ],
            "gap": 1,
        },

        {
            "name": "Mysterious Forest (Misty Garden 2 Field Theme)",
            "parts": [
                "01 Mysterious Forest (Field Front).wav",
                fade_out("01 Mysterious Forest (Field Loop).wav", 96, 6),
            ],
            "gap": 1,
        },

        {
            "name": "Crush & Contort (Misty Garden 2 Battle Theme)",
            "parts": [
                "02 Crush & Contort (Battle Front).wav",
                fade_out("02 Crush & Contort (Battle Loop).wav", 92, 6),
            ],
            "gap": 1,
        },

        {
            "name": "Hope for Existence (The Witch's Theme)",
            "artist": "Cosmograph",
            "parts": [
                "04 Hope for Existence (Boss intro).wav",
                fade_out("04 Hope for Existence (Boss Loop).wav", -10),
            ],
            "gap": 1,
        },

        {
            "name": "Shiranui Battle Theme",
            "artist": "Hox2 (Studio EIM)",
            "parts": [
                "Shiranui_Battle.wav",
                fade_out("Shiranui_Battle.wav", 76, 11),
            ],
            "gap": 1,
        },

        {
            "name": "Encounter Dorchi",
            "artist": "Cosmograph",
            "parts": [
                "SirDorchi.wav",
                fade_out("SirDorchi.wav", 97, 4.8),
            ],
            "gap": 1,
        },

        {
            "name": "Place of Void (Bloody Park 1 Field Theme)",
            "artist": "Selector",
            "parts": [
                fade_out("CA_Field02.wav", 145, 5),
            ],
            "gap": 1,
        },

        {
            "name": "After Revive (Bloody Park 1 Battle Theme)",
            "artist": "Selector",
            "parts": [
                fade_out("CA_Battle02.wav", 149, 5),
            ],
            "gap": 1,
        },

        {
            "name": "Final March of Broken Toys (Bloody Park Boss Theme)",
            "parts": [
                fade_out("CA_Boss02.wav", 110, 5),
            ],
            "gap": 1,
        },

        {
            # This should arguably be "Showtime", but the author also writes it
            # as "Show Time" on the bandcamp page.
            "name": "Show Time (The Joker's Theme)",
            "artist": "Selector",
            "parts": [
                "06 Show Time (Boss Front).wav",
                fade_out("06 Show Time (Boss Loop).wav", -6, 5),
            ],
            "gap": 1,
        },

        {
            "name": "The Phenomenon (Bloody Park 2 Field Theme)",
            "parts": [
                "03 The Phenomenon (Field Front).wav",
                fade_out("03 The Phenomenon (Field Loop).wav", -5),
            ],
            "gap": 1,
        },

        {
            "name": "Obstructor (Bloody Park 2 Battle Theme)",
            "artist": "Selector",
            "parts": [
                "04 Obstructor (Battle Front).wav",
                fade_out("04 Obstructor (Battle Loop).wav", -5),
            ],
            "gap": 1,
        },

        {
            "name": "White Grave Field Theme",
            "parts": [
                fade_out("CA_Field03.wav", -6, 4),
            ],
            "gap": 1,
        },

        {
            "name": "White Grave Battle Theme",
            "parts": [
                fade_out("CA_Battle03.wav", -5),
            ],
            "gap": 1,
        },

        {
            "name": "Near the End (White Grave Boss Theme)",
            "parts": [
                "CA_Boss03_Intro.wav",
                fade_out("CA_Boss03_Loop.wav", -6, 5.25),
            ],
            "gap": 1,
        },

        {
            "name": "Sanctuary",
            "artist": "Selector",
            "parts": [
                "01 Sanctuary (Field Front).wav",
                fade_out("01 Sanctuary (Field Loop).wav", -6.5, 5),
            ],
            "gap": 1,
        },

        {
            "name": "Anxiety",
            "parts": [
                "02 Anxiety (Battle Front).wav",
                fade_out("02 Anxiety (Battle Loop).wav", -10.5, 7.25),
            ],
            "gap": 1,
        },

        {
            "name": "End Of Light",
            "artist": "Cosmograph",
            "parts": [
                "03 End of Light (Boss intro).wav",
                fade_out("02 End of Light (Boss Loop).wav", -13, 10),
            ],
            "gap": 1,
        },

        {
            "name": "Challenge (Early Access Azar Boss Theme)",
            "parts": [
                fade_out("Challenge.wav", -7, 5),
            ],
            "gap": 1,
        },

        {
            "name": "Glitchy Chrono Ark Intro Theme",
            "parts": [
                "ChagedIntro.wav",
            ],
            "gap": 1,
        },

        {
            "name": "Chrono Ark Ex",
            "parts": [
                "choronoArk_ex.wav",
            ],
        },

        {
            "name": "Restart",
            "parts": [
                "ReStart_Intro.wav",
                "ReStart.wav",
                fade_out("ReStart.wav", -10, 8),
            ],
        },

        {
            "name": "Crimson Wilds",
            "parts": [
                fade_out("RW_field.wav", -9),
            ],
            "gap": 1,
        },

        {
            "name": "Crimson Wilds Battle Theme",
            "parts": [
                fade_out("RW_battle.wav", 110, 13.25),
            ],
            "gap": 1,
        },

        {
            "name": "Crimson Wilds Boss Theme",
            "parts": [
                "RW_boss_Intro.wav",
                fade_out("RW_boss.wav", -8, 7),
            ],
            "gap": 1,
        },

        {
            "name": "Azar Boss Theme Phase 1",
            "parts": [
                "Azar_Boss_Theme_Phase1_(Intro).wav",
                "Azar_Boss_Theme_Phase1_(loop).wav",
                fade_out("Azar_Boss_Theme_Phase1_(loop).wav", -5),
            ],
            "gap": 1,
        },

        {
            "name": "Azar Boss Theme Phase 2 (feat. FiNE)",
            "artist": "Lee Dong Hoon (Studio EIM)",
            "lyrics-file": "azar-boss-theme-2-lyrics.txt",
            "parts": [
                volume(
                    fade_out("Azar_Boss_Theme_Phase2_(Intro).wav", -12, 9),
                    0.7,
                ),
            ],
            "gap": 1,
        },

        {
            "name": "Program Master Boss Theme Phase 1",
            "artist": "Rindaman (Studio EIM)",
            "parts": [
                "ProgramMaster_Boss_Theme_Phase1_(Intro).wav",
                fade_out("ProgramMaster_Boss_Theme_Phase1_(Loop).wav", -6, 5),
            ],
            "gap": 1,
        },

        {
            "name": "Program Master Boss Theme Phase 2",
            "artist": "Rindaman (Studio EIM)",
            "parts": [
                "ProgramMaster_Boss_Theme_Phase2_(Intro).wav",
                fade_out("ProgramMaster_Boss_Theme_Phase2_(Loop).wav", -10, 8),
            ],
            "gap": 1,
        },

        {
            "name": "Memory Lane",
            "parts": [
                fade_out("Memory Lane.wav", -8),
            ],
            "gap": 1,
        },

        {
            "name": "Clock Tower Theme",
            "parts": [
                "ClockTower.wav",
                fade_out("ClockTower.wav", -8, 6),
            ],
            "gap": 1,
        },

        {
            "name": "Ark System",
            "parts": [
                "ArkSystemBootUp.wav",
                fade_in("ArkSystemAmbiLoop.wav", 2),
                fade_out("ArkSystemAmbiLoop.wav", -5),
            ],
            "gap": 1,
        },

        {
            "name": "Infinity",
            "parts": [
                "InfinityLoop.wav",
            ],
            "gap": 1,
        },

        {
            "name": "Opposition",
            "parts": [
                "Opposition.wav",
                fade_out("Opposition.wav", -8, 5.5),
            ],
            "gap": 1,
        },

        {
            "name": "Dystopia",
            "parts": [
                "Dystopia_intro.wav",
                fade_out("Dystopia_loop.wav", -6, 5),
            ],
            "gap": 1,
        },

        {
            "name": "Ark Sight",
            "parts": [
                "ArkSight.wav",
                fade_out("ArkSight.wav", -15, 8),
            ],
        },

        {
            "name": "Clone", # TODO: figure out where this is played.
            "parts": [
                "Clone.wav",
                fade_out("Clone.wav", -8, 6.5),
            ],
            "gap": 1,
        },

        {
            "name": "Broken World",
            "artist": "Cosmograph",
            "parts": [
                # TODO: Instead of doubling, maybe extend by 30 seconds.
                "DeeperDeeper.wav",
                fade_out("DeeperDeeper.wav", -5),
            ],
            "gap": 1,
        },

        {
            "name": "Everything Meaning",
            "artist": "Rindaman (Studio EIM)",
            "parts": [
                "EverythingMeaning.wav",
            ],
        },

        {
            "name": "It's Time to Choose",
            "parts": [
                "It's Time to Choose loop.wav",
                "It's Time to Choose climax.wav",
            ]
        },

        {
            # XXX: Should this be "Breakout?"
            "name": "Outbreak",
            "parts": [
                "OutBreak.wav",
                fade_out("OutBreak.wav", -10, 6),
            ],
            "gap": 1,
        },

        {
            "name": "Abyss",
            "parts": [
                "Story_3_Abyss_loop.wav",
                fade_out("Story_3_Abyss_loop.wav", 10, 7),
            ],
            "gap": 1,
        },

        {
            "name": "Story Background Music",
            "parts": [
                "StoryBGM_2.wav",
                fade_out("StoryBGM_2.wav", -3, 0),  # Trim excess silence.
            ],
        },

        {
            "name": "Serious Story Background Music",
            "parts": [
                "StoryBGM_serious.wav",
                fade_out("StoryBGM_serious.wav", -8, 6),
            ],
            "gap": 1,
        },

        {
            "name": "The Legendary Phoenix",
            "artist": "Cosmograph",
            "parts": [
                "pheonix_theme.wav",
                fade_out("pheonix_theme.wav", -7),
            ],
            "gap": 1,
        },

        {
            "name": "There's No Way",
            "parts": [
                "Theres No Way loop_Intro.wav",
                fade_out("Theres No Way loop.wav", -5),
            ],
            "gap": 1,
        },

        {
            "name": "Virtual Emotions",
            "parts": [
                "VirtualEmotions.wav",
                fade_out("VirtualEmotions.wav", -10, 7.5),
            ],
            "gap": 1,
        },

        {
            "name": "Wrong Beginning",
            "artist": "Selector",
            "parts": [
                "Wrong Beginning (Front).wav",
                fade_out("Wrong Beginning (Loop).wav", -10, 7.7),
            ],
        },

        {
            "name": "End Credits Background Music",
            "artist": "KuaNu (Studio EIM)",
            "parts": [
                "TrueEndCredit_BGM.wav",
            ],
        },
    ]

    for trackno, track in enumerate(tracks, 1):
        build_track(output_directory, track, trackno)

    print("Done processing tracks.")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
