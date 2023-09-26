import os
from datetime import datetime

import whisper
from dotenv import load_dotenv
from huggingsound import SpeechRecognitionModel
from pytube import YouTube
from urllib.parse import urlparse, parse_qs
from pydub import AudioSegment

from utils.GlobalLogger import log_info
from utils.file_management import save_list_to_file, save_str_to_file


class YouTubeTranscriber:
    def __init__(self, url, timestamp):
        self.url = url
        self.video_id = f"{timestamp}_{self.extract_video_id(url)}"

        self.video_filename = f"{self.video_id}.3gpp"
        self.video_output_path = os.path.join('assets', 'youtube_videos')
        os.makedirs(self.video_output_path, exist_ok=True)
        self.video_file_path = os.path.join(self.video_output_path, self.video_filename)

        self.text_filename = f"{self.video_id}.txt"
        self.text_output_path = os.path.join('assets', 'transcriptions')
        os.makedirs(self.text_output_path, exist_ok=True)
        self.text_file_path = os.path.join(self.text_output_path, self.text_filename)

        self.transcriber = Transcriber()

    @staticmethod
    def extract_video_id(url):
        query = urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                return p['v'][0]
        return None

    def download_video(self):
        if self.video_id is None:
            raise ValueError("Invalid YouTube URL")

        path = YouTube(self.url).streams.first().download(output_path=self.video_output_path,
                                                          filename=self.video_filename)
        if self.video_file_path not in path:
            raise ValueError(f"Video downloaded to incorrect location: {path}\nExpected: {self.video_file_path}")

        # AudioConverter(self.video_file_path).convert("wav")
        os.system(f'ffmpeg -i {self.video_file_path} {self.video_file_path.split(".")[0] + ".wav"}')
        self.video_file_path = self.video_file_path.split(".")[0] + ".wav"

    def transcribe(self):
        transcriptions = self.transcriber.transcribe(self.video_file_path)

    def save_to_file(self, transcriptions):
        if type(transcriptions) is list:
            save_list_to_file(self.text_file_path, transcriptions)
        else:
            save_str_to_file(self.text_file_path, transcriptions)


class AudioConverter:
    def __init__(self, input_file):
        self.input_file = input_file

    def convert(self, output_format):
        if not os.path.exists(self.input_file):
            raise FileNotFoundError("Input file does not exist")

        if output_format not in ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm']:
            raise ValueError("Invalid output format. Must be one of: mp3, mp4, mpeg, mpga, m4a, wav, webm")

        # Load 3gpp file
        audio = AudioSegment.from_file(self.input_file, format="3gpp")

        # Define output file name
        base, ext = os.path.splitext(self.input_file)
        output_file = f"{base}.{output_format}"

        # Export audio in the desired format
        audio.export(output_file, format=output_format)
        print(f"File has been converted to {output_file}")
        return output_file


class Transcriber:

    def __init__(self):
        """
        This class is responsible for transcribing audio files. It uses the whisper or huggingface models for local
        transcription based on the config.
        """
        self.model_source = self._get_model_source()
        self.model = self._get_model()

    def transcribe(self, audio_paths, fp16=False):
        if self.model_source == 'whisper':
            transcriptions = self.model.transcribe(audio_paths, fp16=fp16)
        else:
            transcriptions = self.model.transcribe(audio_paths)
        log_info('Transcription done.')
        return self.get_texts(transcriptions)

    def _get_model_source(self):
        model_source = os.getenv("TRANSCRIPTION_MODEL_SOURCE")
        if model_source not in ["whisper", "huggingface"]:
            raise ValueError("TRANSCRIPTION_MODEL_SOURCE must be either 'whisper' or 'huggingface'")
        return model_source

    def _get_model(self):
        if self.model_source == "whisper":
            model_path = os.path.join("src", "whisper_model", "base.pt")
            if os.path.exists(model_path):
                log_info('Load local model.')
                return whisper.load_model(model_path)
            log_info('Load model from web.')
            return whisper.load_model('base')
        elif self.model_source == "huggingface":
            log_info('Load model from web.')
            return SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-english")

    def get_texts(self, transcriptions):
        if self.model_source == "whisper":
            return transcriptions["text"]
        elif self.model_source == "huggingface":
            return transcriptions


if __name__ == "__main__":
    load_dotenv()
    url = 'https://www.youtube.com/watch?v=HrCIWSUXRmo'
    try:
        transcriber = YouTubeTranscriber(url, datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        # transcriber.download_video()
        transcriber.transcribe()
        print(f"Text file: {transcriber.text_file_path};\nVideo file: {transcriber.video_file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
