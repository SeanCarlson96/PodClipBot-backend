import os
import speech_recognition as sr
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.all import *
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import textwrap


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

    # Split the subtitles into chunks based on the timing of the words
    subs_per_sec = len(subtitles_text) / video.duration
    subs = subtitles_text.split()
    num_subs = len(subs)
    subs_per_sec = num_subs / audio.duration
    chunks = []
    chunk = ''
    i = 0
    while i < num_subs:
        if chunk == '':
            start_time = i / subs_per_sec
        if len(chunk.split()) < 10:
            chunk += subs[i] + ' '
            i += 1
        else:
            end_time = i / subs_per_sec
            chunks.append((start_time, end_time, chunk))
            chunk = ''
    if chunk != '':
        end_time = num_subs / subs_per_sec
        chunks.append((start_time, end_time, chunk))

    # Create the SRT file for all subtitles
    srt_filename = os.path.splitext(video.filename)[0] + '.srt'
    with open(srt_filename, 'w') as f:
        for i, (start_time, end_time, sub) in enumerate(chunks):
            start_time_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(int(start_time / 3600), int((start_time / 60) % 60), int(start_time % 60), int(start_time * 1000 % 1000))
            end_time_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(int(end_time / 3600), int((end_time / 60) % 60), int(end_time % 60), int(end_time * 1000 % 1000))
            timestamp = '{} --> {}'.format(start_time_str, end_time_str)
            f.write('{}\n{}\n{}\n\n'.format(i+1, timestamp, sub))

    # Create the subtitle clip
    print(video.size)
    print(video.w)
    generator = lambda txt: TextClip(txt, font='Arial', fontsize=120, color='white', stroke_width=1, stroke_color='black', method='caption', size=video.size).set_position('center')
    subtitle_clip = SubtitlesClip(srt_filename, generator)

    # Add the subtitles to the video
    video_with_subtitles = CompositeVideoClip([video, subtitle_clip.set_duration(video.duration)])

    # Write the video with subtitles to a new file
    video_with_subtitles_file = os.path.splitext(video.filename)[0] + '_subtitled.mp4'
    video_with_subtitles.duration = video.duration
    video_with_subtitles.write_videofile(video_with_subtitles_file)

    # Return the resulting video clip with subtitles
    return video_with_subtitles
