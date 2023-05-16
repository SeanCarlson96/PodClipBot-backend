import os
import whisper
import whisperx
from moviepy.editor import TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from functions.srt_format_timestamp import srt_format_timestamp

# This version just shows one word at a time as it is being spoken
def add_subtitles(video):

    # Extract the audio from the video
    audio = video.audio
    audio_filename = os.path.splitext(video.filename)[0] + '.wav'
    audio.write_audiofile(audio_filename)

    device = "cpu"

    # Get transcription segments using whisper
    model = whisperx.load_model("medium", device)
    result = model.transcribe(audio_filename)
    # segments = result['segments']

    # load alignment model and metadata
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

    # align whisper output
    result_aligned = whisperx.align(result["segments"], model_a, metadata, audio_filename, device)

    # print(result_aligned["segments"]) # after alignment
    # print(result_aligned["word_segments"]) # after alignment

    segments = result_aligned['word_segments']
    # Clear the contents of the .srt file
    srt_filename = os.path.splitext(video.filename)[0] + '.srt'
    with open(srt_filename, 'w', encoding='utf-8') as srtFile:
        srtFile.write('')

    # Write the segments from whisper result into srt format
    with open(srt_filename, 'a', encoding='utf-8') as srtFile:
        for idx, segment in enumerate(segments):
            startTime = srt_format_timestamp(segment['start'])
            endTime = srt_format_timestamp(segment['end'])
            text = segment['text']
            segmentId = idx+1
            segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"
            srtFile.write(segment)

    # Create the subtitle clip
    generator = lambda txt: TextClip(txt, font='Helvetica-BoldOblique', fontsize=150, color='white', stroke_width=1, stroke_color='black', method='caption', size=video.size).set_position((0.5,0.2), relative=True)
    subtitle_clip = SubtitlesClip(srt_filename, generator)

    # Add the subtitles to the video
    video_with_subtitles = CompositeVideoClip([video, subtitle_clip.set_duration(video.duration)])
    return video_with_subtitles
