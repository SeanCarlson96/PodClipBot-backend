import os
import speech_recognition as sr
from moviepy.editor import *

def add_subtitles(video):

    # Extract the audio from the video
    audio = video.audio
    audio_filename = os.path.splitext(video.filename)[0] + '.wav'
    audio.write_audiofile(audio_filename)

    # Set the duration of the audio file to match the video
    audio.duration = video.duration

    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Transcribe the audio using Google Speech Recognition
    with sr.AudioFile(audio_filename) as source:
        audio_data = recognizer.record(source)
        subtitles_text = recognizer.recognize_google(audio_data)

    # Create the subtitle clip
    subtitles = TextClip(subtitles_text, fontsize=100, color='yellow').set_position(('center', 'center'))

    # Add the subtitles to the video
    video_with_subtitles = CompositeVideoClip([video, subtitles])

    # Write the video with subtitles to a new file
    video_with_subtitles_file = os.path.splitext(video.filename)[0] + '_subtitled.mp4'
    video_with_subtitles.duration = video.duration
    video_with_subtitles.write_videofile(video_with_subtitles_file)

    # Return the resulting video clip with subtitles
    return video_with_subtitles
