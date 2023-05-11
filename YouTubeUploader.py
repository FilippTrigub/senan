import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_video_to_youtube(file_path, title, description, category, privacy):
    # Authenticate with YouTube Data API
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=os.getenv('CLIENT_SECRETS_FILE_PATH'),
                                                     scopes=['https://www.googleapis.com/auth/youtube.upload'])
    credentials = flow.run_local_server(port=0)
    client = build('youtube', 'v3', credentials=credentials)

    # Create a new video resource
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': category
        },
        'status': {
            'privacyStatus': privacy
        }
    }

    try:
        # Upload the video using the YouTube API
        insert_request = client.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(file_path)
        )
        response = insert_request.execute()

        # Return the video ID
        video_id = response['id']
        print(f"Video uploaded successfully with ID {video_id}")
        return video_id

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

