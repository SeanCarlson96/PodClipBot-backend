import os
import random
import tempfile
from moviepy.editor import *
from pydub import AudioSegment

def add_background_music(video, clip_info):
    music_folder = "music"
    music_files = [os.path.join(music_folder, f) for f in os.listdir(music_folder) if f.endswith(".mp3")]
    

    volume_value = int(clip_info.get('volume', 50))
    music_choice = clip_info.get('musicChoice', 'random')
    custom_upload = clip_info.get('music-file', None)
    fade_in_and_out = clip_info.get('musicFade', 'on')
    music_duration = clip_info.get('musicDuration', 'full')

    if music_choice == 'random' or not music_choice:
        music_file = random.choice(music_files)
    else:
        music_file = os.path.join(music_folder, music_choice)

    music = AudioSegment.from_mp3(music_file)
    video_audio = AudioSegment.from_file("temp.wav")


    default_volume = 50
    volume_adjustment = (volume_value - default_volume) / (100 - default_volume) * 9
    # Adjust the volumes
    music = music + volume_adjustment - 6

    # Set the music duration to match the video's duration
    # video_duration_ms = video.duration * 1000
    # music = music[:video_duration_ms]
    music = music[:video.duration * 1000]

    # Add fade in and fade out effects to the background music
    music = music.fade_in(1500).fade_out(1500)

    # Combine the audio tracks
    combined_audio = video_audio.overlay(music)

    # Export the combined audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        combined_audio.export(temp_audio.name, format="mp3")

        # Set the combined audio to the video
        video_with_music = video.set_audio(AudioFileClip(temp_audio.name))

    # Delete the temporary audio file
    os.remove(temp_audio.name)

    return video_with_music
