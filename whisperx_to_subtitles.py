import os
import whisperx
from moviepy.editor import TextClip
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from srt_format_timestamp import srt_format_timestamp

def add_subtitles(video, audio_filename):

    device = "cpu"

    # Get transcription segments using whisper
    model = whisperx.load_model("tiny", device)
    result = model.transcribe(audio_filename)
    # segments = result['segments']

    # load alignment model and metadata
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

    # align whisper output
    result_aligned = whisperx.align(result["segments"], model_a, metadata, audio_filename, device)

    segments = result_aligned['word_segments']

    # Clear the contents of the .srt file
    srt_filename = os.path.splitext(video.filename)[0] + '.srt'
    with open(srt_filename, 'w', encoding='utf-8') as srtFile:
        srtFile.write('')

    # Write the segments from whisper result into srt format
    with open(srt_filename, 'a', encoding='utf-8') as srtFile:
        textsegment = ''
        wordnumber = 1
        for idx, segment in enumerate(segments):
            currentword = segment['text']
            # build textsegments up to a specific character count. set at 10 right now
            if len(textsegment) == 0:
                startTime = srt_format_timestamp(segment['start'])
                segmentId = idx+1
            if len(textsegment) < 10:
                if wordnumber == 1:
                    textsegment = currentword
                else:
                    textsegment = textsegment + ' ' + currentword
                wordnumber = wordnumber + 1
                # if we've reached the last segment in our list, write the final
                # srt chunk even if it is not long enough
                if idx+1 == len(segments):
                    endTime = srt_format_timestamp(segment['end'])
                    segment = f"{segmentId}\n{startTime} --> {endTime}\n{textsegment}\n\n"
                    srtFile.write(segment)
                else:
                    # If the start time of the next word minus the end time of
                    # the current word is greater than .5 seconds, write the segment
                    # as is
                    nextSegment = segments[idx+1]
                    timeBetweenWords = nextSegment['start'] - segment['end']
                    if timeBetweenWords > 0.5:
                        endTime = srt_format_timestamp(segment['end'])
                        segment = f"{segmentId}\n{startTime} --> {endTime}\n{textsegment}\n\n"
                        srtFile.write(segment)
                        textsegment = ''
                        wordnumber = 1
            else:
                endTime = srt_format_timestamp(segment['end'])
                segment = f"{segmentId}\n{startTime} --> {endTime}\n{textsegment + ' ' + currentword}\n\n"
                srtFile.write(segment)
                textsegment = ''
                wordnumber = 1
    
    # Create the subtitle clip
    # generator = lambda txt: TextClip(txt, font='Helvetica-BoldOblique', fontsize=150, color='white', stroke_width=1, stroke_color='black', method='caption', size=video.size).set_position((0.5,0.2), relative=True)
    generator = lambda txt: TextClip(
                                    txt, 
                                    font='Helvetica-BoldOblique', 
                                    fontsize=150, 
                                    color="white", 
                                    bg_color="black", 
                                    stroke_width=1, 
                                    stroke_color="black", 
                                    method='label', 
                                    )
    subtitle_clip = SubtitlesClip(srt_filename, generator).set_position(('center',0.66), relative=True)


    # Add the subtitles to the video
    video_with_subtitles = CompositeVideoClip([video, subtitle_clip.set_duration(video.duration)])
    return video_with_subtitles
