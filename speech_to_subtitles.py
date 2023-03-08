import speech_recognition as sr
import pysrt
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.editor import VideoFileClip, AudioFileClip

def add_subtitles(video):
    # Extract audio from the video
    audio_filename = video.audio.filename
    audio = AudioFileClip(audio_filename)
    
    # Use speech recognition to generate subtitles
    recognizer = sr.Recognizer()
    with audio.write_audiofile("temp_audio.wav", fps=44100) as wav_file:
        recognizer.adjust_for_ambient_noise(audio)
        audio_file = sr.AudioFile("temp_audio.wav")
        transcript = recognizer.recognize_google(audio_file)
    
    # Create the SubRip file object for the subtitles
    subtitle_file = pysrt.SubRipFile()
    subtitle_file.append(pysrt.SubRipItem(
        index=1,
        start=pysrt.SubRipTime(0, 0, 0),
        end=pysrt.SubRipTime(0, 0, 5),
        text=transcript
    ))
    
    # Create the SubtitlesClip object and add it to the video clip
    subtitles = SubtitlesClip(subtitle_file)
    video_with_subtitles = video.set_audio(None).set_duration(subtitles.duration).set_fps(30).set_audio(subtitles)
    
    return video_with_subtitles
