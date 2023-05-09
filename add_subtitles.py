import os
import pprint
import traceback
import whisperx
import gc 
from moviepy.editor import TextClip
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from srt_format_timestamp import srt_format_timestamp

def add_subtitles(video, audio_filename, clip_info):

    font = clip_info.get('font', 'Arial')
    font_size = 10 * int(clip_info.get('fontSize', '15'))
    subtitle_color = clip_info.get('subtitleColor', '#ffffff')
    subtitle_background = clip_info.get('subtitleBackgroundToggle', 'off')
    subtitle_background_color = clip_info.get('subtitleBackgroundColor', 'black') if subtitle_background == 'true' else None
    background_color = subtitle_background_color if subtitle_background_color else 'transparent'

    font_stroke_width = int(clip_info.get('strokeWidth', '0'))
    font_stroke_color = clip_info.get('strokeColor', 'black')
    if font_stroke_width == 0:
        font_stroke_color = None
    position_horizontal = clip_info.get('subtitlePositionHorizontal', 'center')
    position_vertical = ((100 - int(clip_info.get('subtitlePositionVertical', '35'))) / 100)
    # whisperx_model = clip_info.get('whisperXModel', 'tiny')
    segment_length = int(clip_info.get('subtitleSegmentLength', '10'))
    diarization = clip_info.get('diarizationToggle', 'off')
    
    # Get transcription segments using whisper
    device = "cpu"
    audio_file = audio_filename
    batch_size = 16 # reduce if low on GPU mem
    compute_type = "int8" #try changing to float16 after development

    # model = whisperx.load_model("large-v2", device, compute_type=compute_type)
    model = whisperx.load_model("large-v2", device, compute_type=compute_type, language='en')

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)
    # segments = result['segments']

    # load alignment model and metadata
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

    # align whisper output
    result_aligned = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    
    segments = result_aligned['word_segments']
    # pprint(result_aligned)


    # hf_token = os.environ["HF_TOKEN"]
    # # 3. Assign speaker labels
    # diarize_model = whisperx.DiarizationPipeline(use_auth_token=hf_token, device=device)

    # # add min/max number of speakers if known
    # diarize_segments = diarize_model(audio_file)
    # # diarize_model(audio_file, min_speakers=min_speakers, max_speakers=max_speakers)

    # result = whisperx.assign_word_speakers(diarize_segments, result)
    # pprint(diarize_segments)
    # pprint(result["segments"]) # segments are now assigned speaker IDs



    # Clear the contents of the .srt file
    srt_filename = os.path.splitext(video.filename)[0] + '.srt'
    with open(srt_filename, 'w', encoding='utf-8') as srtFile:
        srtFile.write('')

    # Write the segments from whisper result into srt format
    with open(srt_filename, 'a', encoding='utf-8') as srtFile:
        textsegment = ''
        wordnumber = 1
        for idx, segment in enumerate(segments):
            currentword = segment['word']
            # build textsegments up to a specific character count. set at 10 right now
            if len(textsegment) == 0:
                startTime = srt_format_timestamp(segment['start'])
                segmentId = idx+1
            # if len(textsegment) < 10:
            if len(textsegment) < segment_length:
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
                                    font=font, 
                                    fontsize=font_size, 
                                    color=subtitle_color, 
                                    bg_color=background_color, 
                                    stroke_width=font_stroke_width, 
                                    stroke_color=font_stroke_color, 
                                    method='label', 
                                    )
    subtitle_clip = SubtitlesClip(srt_filename, generator).set_position((position_horizontal,position_vertical), relative=True)

    # Add the subtitles to the video
    video_with_subtitles = CompositeVideoClip([video, subtitle_clip.set_duration(video.duration)])
    return video_with_subtitles
