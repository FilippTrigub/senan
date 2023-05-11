# This is a sample Python script.
from dotenv import load_dotenv

from ContentCreator import ContentCreator
from YouTubeUploader import upload_video_to_youtube

if __name__ == '__main__':
    UPLOAD = False

    load_dotenv()

    content_creator = ContentCreator()
    filename = content_creator.create()

    if UPLOAD:
        # the category id 24 is Entertainment
        upload_video_to_youtube(filename, content_creator.query, f'What people think about {content_creator.query}.',
                                category=24, privacy='Private')
