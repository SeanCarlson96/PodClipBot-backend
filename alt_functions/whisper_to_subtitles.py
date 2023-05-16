import os
import whisper
from moviepy.editor import TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from functions.srt_format_timestamp import srt_format_timestamp

def add_subtitles(video):

    # Extract the audio from the video
    audio = video.audio
    audio_filename = os.path.splitext(video.filename)[0] + '.wav'
    audio.write_audiofile(audio_filename)

    # Get transcription segments using whisper
    model = whisper.load_model("base")
    result = model.transcribe(audio_filename)
    segments = result['segments']

    # Clear the contents of the .srt file
    srt_filename = os.path.splitext(video.filename)[0] + '.srt'
    with open(srt_filename, 'w', encoding='utf-8') as srtFile:
        srtFile.write('')

    # Write the segments from whisper result into srt format
    with open(srt_filename, 'a', encoding='utf-8') as srtFile:
        for segment in segments:
            startTime = srt_format_timestamp(segment['start'])
            endTime = srt_format_timestamp(segment['end'])
            text = segment['text']
            segmentId = segment['id']+1
            segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"
            srtFile.write(segment)

    # Create the subtitle clip
    generator = lambda txt: TextClip(txt, font='Helvetica-BoldOblique', fontsize=150, color='white', stroke_width=1, stroke_color='black', method='caption', size=video.size).set_position((0.5,0.2), relative=True)
    subtitle_clip = SubtitlesClip(srt_filename, generator)

    # Add the subtitles to the video
    video_with_subtitles = CompositeVideoClip([video, subtitle_clip.set_duration(video.duration)])
    return video_with_subtitles
