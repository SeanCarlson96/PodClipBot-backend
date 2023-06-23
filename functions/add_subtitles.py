# import glob
import os
# import pprint
# import traceback
import whisperx
# import gc 
from moviepy.editor import TextClip
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from functions.fill_missing_times import fill_missing_times
from functions.srt_format_timestamp import srt_format_timestamp
# from diarized_subtitles import diarized_subtitles
from functions.diarized_subtitles2 import diarized_subtitles
from functions.adjust_word_timestamps import adjust_word_timestamps
from functions.profanity_filter import check_profanity

def send_progress_update(socketio, progress, socket_id):
    socketio.emit('video_processing_progress', {'progress': progress}, room=socket_id)

def add_subtitles(tempdir, video, audio_filename, clip_info, socketio, socket_id):

    send_progress_update(socketio, 3, socket_id)

    font = clip_info.get('font', 'Arial-Bold-Italic')
    font_size = int(clip_info.get('fontSize', '15')) * 3
    subtitle_color = clip_info.get('subtitleColor', '#ffffff')
    subtitle_background = clip_info.get('subtitleBackgroundToggle', 'off')
    subtitle_background_color = clip_info.get('subtitleBackgroundColor', 'black') if subtitle_background == 'true' else None
    background_color = subtitle_background_color if subtitle_background_color else 'transparent'

    font_stroke_width = int(clip_info.get('strokeWidth', '0'))
    font_stroke_color = clip_info.get('strokeColor', 'black')
    if font_stroke_width == 0:
        font_stroke_color = None

    position_horizontal = clip_info.get('subtitlePositionHorizontal', 'center').lower()

    position_vertical = ((100 - int(clip_info.get('subtitlePositionVertical', '35'))) / 100)
    # whisperx_model = clip_info.get('whisperXModel', 'tiny')
    segment_length = int(clip_info.get('subtitleSegmentLength', '10'))
    diarization = clip_info.get('diarizationToggle', None)

    videoDuration = video.duration
    
    send_progress_update(socketio, 6, socket_id)
    # Get transcription segments using whisper
    device = "cpu"
    audio_file = audio_filename
    batch_size = 16 # reduce if low on GPU mem
    compute_type = "int8" #try changing to float16 after development

    # model = whisperx.load_model("large-v2", device, compute_type=compute_type)
    
    send_progress_update(socketio, 9, socket_id)
    model = whisperx.load_model("large-v2", device, compute_type=compute_type, language='en')
    
    send_progress_update(socketio, 12, socket_id)
    # print('after whisperx.load_model')
    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)
    print(result)
    # load alignment model and metadata
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

    send_progress_update(socketio, 15, socket_id)
    # align whisper output
    # result_align = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=True)
    result_aligned = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)


    # result_aligned = adjust_word_timestamps(result_align) # hopefully temporary solution until Max Bain gets back to my email? we will see
    # print(result_aligned)


    send_progress_update(socketio, 18, socket_id)
    
    if diarization:
        socketio.emit('build_action', {'action': 'Diarizing'}, room=socket_id)
        video_with_subtitles = diarized_subtitles(tempdir, socketio, clip_info, device, audio_file, result_aligned, segment_length, video, font, font_size, subtitle_color, background_color, font_stroke_width, font_stroke_color, position_horizontal, position_vertical, socket_id)
    else:
        segments = result_aligned['word_segments']
        print('not diarized')
        segments = fill_missing_times(segments, videoDuration)

        # print(segments)
        # print(result_aligned)
        # Clear the contents of the .srt file
        # srt_filename = os.path.splitext(video.filename)[0] + '.srt'
        srt_filename = os.path.join(tempdir, os.path.splitext(video.filename)[0] + '.srt')
        with open(srt_filename, 'w', encoding='utf-8') as srtFile:
            srtFile.write('')
        # Write the segments from whisper result into srt format
        with open(srt_filename, 'a', encoding='utf-8') as srtFile:
            textsegment = ''
            wordnumber = 1

            for idx, segment in enumerate(segments):
                # currentword = segment['word']
                currentword = check_profanity(segment['word'])
                # build textsegments up to a specific character count
                # print(segment)

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
                        if timeBetweenWords > 0.3:
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
