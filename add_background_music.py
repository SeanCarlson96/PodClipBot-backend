import os
import random
import tempfile
from moviepy.editor import *
from pydub import AudioSegment

def add_background_music(video, video_file_path):
    music_folder = "music"
    music_files = [os.path.join(music_folder, f) for f in os.listdir(music_folder) if f.endswith(".mp3")]

    music_file = random.choice(music_files)

    music = AudioSegment.from_mp3(music_file)
    video_audio = AudioSegment.from_file("temp.wav")

    # Adjust the volumes
    # video_audio = video_audio - 6  # Reduce video audio volume by 6 dB
    music = music - 6             # Increase music volume by 4 dB

    # Set the music duration to match the video's duration
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
