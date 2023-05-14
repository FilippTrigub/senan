from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep


def save_text_to_mp3(content_object):
    """Saves Text to MP3 files.

    Args:
        content_object : contains graphs and other content
    """
    print_step("Saving Text to MP3 files...")
    total_audio_duration = 0
    audio_durations_per_statistic = []

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    for key, content_item in content_object.items():
        tts = gTTS(text=content_item["text"], lang="en", slow=False)
        tts.save(f"assets/mp3/{key}.mp3")
        audio_durations_per_statistic.append(MP3(f"assets/mp3/{key}.mp3").info.length)
        total_audio_duration += audio_durations_per_statistic[-1]

    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return total_audio_duration, audio_durations_per_statistic
