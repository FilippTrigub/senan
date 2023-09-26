# This is a sample Python script.
import argparse
import os

from dotenv import load_dotenv

from ContentCreator import ContentCreator
from LLMPoweredContentCreator import LLMPoweredContentCreator
from YouTubeUploader import upload_video_to_youtube


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=("SENAN - Sentiment Analysis and Content Creation."),
        epilog="Designed by Trigub"
    )
    parser.add_argument('--llm', '-l',
                        type=bool,
                        default=True,
                        help='Use LLM to create output. Default is True'
                        )
    return parser.parse_args()


if __name__ == '__main__':
    UPLOAD = False

    load_dotenv()

    if os.getenv('USE_LLM'):
        content_creator = LLMPoweredContentCreator()
    else:
        content_creator = ContentCreator()

    text_filename, video_filename = content_creator.create()

    print(f"Text saved to {text_filename}.\nVideo saved to {video_filename}.")

    if UPLOAD:
        # the category id 24 is Entertainment
        upload_video_to_youtube(video_filename,
                                content_creator.query,
                                f'What people think about {content_creator.query}.',
                                category=24, privacy='Private')
        print("Upload done.")
