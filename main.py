# This is a sample Python script.
from dotenv import load_dotenv

from ContentCreator import ContentCreator
from YouTubeUploader import upload_video_to_youtube


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_dotenv()
    content_creator = ContentCreator()
    filename = content_creator.create()

    upload_video_to_youtube(filename, content_creator.query, f'What people think about {content_creator.query}.',
                            category='Entertainment', privacy='Private')
    # upload_video_to_youtube('C:\\coding_challanges\\sentimental_twitter\\assets\\2023_04_16_19_38_06_senan.mp4',
    #                         'Ukraine', f'What people think about Ukraine.',
    #                         category='Entertainment', privacy='Private')
