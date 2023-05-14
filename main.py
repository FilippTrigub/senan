# This is a sample Python script.
import argparse

from dotenv import load_dotenv

from ContentCreator import ContentCreator
from LLMPoweredContentCreator import LLMPoweredContentCreator
from YouTubeUploader import upload_video_to_youtube


def parse_arguements():
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
    args = parse_arguements()

    if args.llm:
        content_creator = LLMPoweredContentCreator()
    else:
        content_creator = ContentCreator()

    filename = content_creator.create()

    if UPLOAD:
        # the category id 24 is Entertainment
        upload_video_to_youtube(filename, content_creator.query, f'What people think about {content_creator.query}.',
                                category=24, privacy='Private')
