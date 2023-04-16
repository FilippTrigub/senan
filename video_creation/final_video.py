from datetime import datetime
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeAudioClip,
    CompositeVideoClip,
)
import re

from moviepy.video.VideoClip import TextClip

from utils.console import print_step
from dotenv import load_dotenv
import os

W, H = 1080, 1920


def create_folders_if_necessary(path):
    if not os.path.exists(path):
        subpath, filename = os.path.split(path)
        if '/' in subpath:
            create_folders_if_necessary(subpath)
        try:
            os.mkdir(subpath)
        except FileExistsError:
            pass


def save_figure_if_graph(content_item, image_path):
    if os.path.exists(image_path):
        os.remove(image_path)
    content_item['graph'].figure.savefig(image_path)


def make_final_video(content_object):
    opacity, background_clip = _prepare_video()
    # Gather all audio clips and all images
    audio_clips = []
    video_clips = []
    create_folders_if_necessary('assets/png')
    for key, content_item in content_object.items():
        audio_clips.append(AudioFileClip(f"assets/mp3/{key}.mp3"))
        image_path = f"assets/png/{key}.png"
        if content_item.keys().__len__() == 1:
            # Intro clip
            video_clips.append(
                TextClip(content_item['text'], fontsize=70, color='black', bg_color='white', size=(W - 100, H),
                         method='caption')
                .set_position(('center', 'bottom'))
                .set_duration(audio_clips[-1].duration)
                .set_opacity(float(opacity))
                )
        else:
            if 'graph' in content_item.keys():
                save_figure_if_graph(content_item, image_path)
            video_clips.append(
                ImageClip(image_path)
                .set_duration(audio_clips[-1].duration)
                .set_position("center")
                .resize(width=W - 100)
                .set_opacity(float(opacity)),
            )
    filename = _save_video(audio_clips, video_clips, background_clip)
    return filename


def make_final_video_with_gpt(content_object):
    opacity, background_clip = _prepare_video()
    # Gather all audio clips and all images
    audio_clips = []
    video_clips = []
    create_folders_if_necessary('assets/png')

    # get gpt item and total duration of gpt text
    gpt_item_key = content_object.keys()[-1]
    gpt_content_item = content_object[gpt_item_key]
    gpt_audio_clip = AudioFileClip(f"assets/mp3/{gpt_content_item}.mp3")
    total_duration = gpt_audio_clip.duration

    # get all other items and estimate their individual audio duration
    intro_duration = AudioFileClip(f"assets/mp3/{content_object.items()[0]}.mp3").duration
    # individual duration is the duration of each content part excluding intro, outro and gpt
    individual_duration = (total_duration - intro_duration) / (len(content_object.items()) - 3)
    for key, content_item in content_object.items():
        image_path = f"assets/png/{key}.png"
        if key == content_object.keys()[0]:
            # Intro clip
            video_clips.append(TextClip(content_item['text'], fontsize=70, color='black', bg_color='white')
                               .set_position(('center', 'bottom'))
                               .set_duration(audio_clips[-1].duration)
                               .set_opacity(float(opacity))
                               )
        if content_item.keys().__len__() == 2:
            # not outro or gpt
            if 'graph' in content_item.keys():
                save_figure_if_graph(content_item, image_path)
            video_clips.append(
                ImageClip(image_path)
                .set_duration(individual_duration)
                .set_position("center")
                .resize(width=W - 100)
                .set_opacity(float(opacity)),
            )

    filename = _save_video(audio_clips, video_clips, background_clip)
    return filename


def _save_video(audio_clips, video_clips, background_clip):
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    audio_concat = concatenate_audioclips(audio_clips)
    audio_composite = CompositeAudioClip([audio_concat])
    video_concat = concatenate_videoclips(video_clips).set_position(
        ("center", "center")
    )
    video_concat.audio = audio_composite
    final = CompositeVideoClip([background_clip, video_concat])
    filename = (re.sub('[?\"%*:|<>]', '', ("assets/" + timestamp + "_senan.mp4")))
    final.write_videofile(filename, fps=45, audio_codec="aac", audio_bitrate="192k")
    return filename


def _prepare_video():
    # Calls opacity from the .env
    load_dotenv()
    opacity = 1

    print_step("Creating the final video...")

    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)

    background_clip = (
        VideoFileClip("assets/mp4/clip.mp4")
        .without_audio()
        .resize(height=H)
        .crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
    )
    return opacity, background_clip
