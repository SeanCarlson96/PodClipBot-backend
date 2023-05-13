import glob
import os
import whisperx
from moviepy.editor import TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from srt_format_timestamp import srt_format_timestamp

def create_subtitle_clip(srt_filename, color, font, font_size, background_color, font_stroke_width, font_stroke_color, position_horizontal, position_vertical, video):
    generator = lambda txt: TextClip(
        txt,
        font=font,
        fontsize=font_size,
        color=color,
        bg_color=background_color,
        stroke_width=font_stroke_width,
        stroke_color=font_stroke_color,
        method='label',
    )
    subtitle_clip = SubtitlesClip(srt_filename, generator).set_position((position_horizontal,position_vertical), relative=True)
    return subtitle_clip.set_duration(video.duration)

def assign_speaker(words):
    last_speaker = None

    # First pass: from start to end
    for word in words:
        if "speaker" in word:
            last_speaker = word["speaker"]
        elif last_speaker is not None:
            word["speaker"] = last_speaker

    # Second pass: from end to start
    last_speaker = None
    for word in reversed(words):
        if "speaker" in word:
            last_speaker = word["speaker"]
        elif last_speaker is not None:
            word["speaker"] = last_speaker

    return words

def diarized_subtitles(socketio, clip_info, device, audio_file, result_aligned, segment_length, video, font, font_size, subtitle_color, background_color, font_stroke_width, font_stroke_color, position_horizontal, position_vertical):
    hf_token = os.environ["HF_TOKEN"]

    socketio.emit('video_processing_progress', {'progress': 21})

    diarize_model = whisperx.DiarizationPipeline(use_auth_token=hf_token, device=device)
    diarize_segments = diarize_model(audio_file) # this is the line that takes a long time

    socketio.emit('video_processing_progress', {'progress': 30})

    result = whisperx.assign_word_speakers(diarize_segments, result_aligned)
    segments = result['word_segments']
    # print(result)

    segments = assign_speaker(segments)
    # print(segments)

    srt_files = glob.glob('*.srt')
    for srt_filename in srt_files:
        with open(srt_filename, 'w', encoding='utf-8') as srtFile:
            srtFile.write('')

    speakers = {}
    for segment in segments:
        if 'speaker' in segment:
            speaker = segment['speaker']
            if speaker not in speakers:
                speakers[speaker] = []
            speakers[speaker].append(segment)
        else:
            print(f"Warning: 'speaker' key not found in segment: {segment}")

    for speaker, speaker_segments in speakers.items():
        srt_filename = f"{speaker}.srt"
        with open(srt_filename, 'a') as srtFile:
            pass
        with open(srt_filename, 'w', encoding='utf-8') as srtFile:
            textsegment = ''
            wordnumber = 1
            current_speaker = None
            for idx, segment in enumerate(speaker_segments):
                currentword = segment['word']
                new_speaker = segment['speaker'] if 'speaker' in segment else None

                if len(textsegment) == 0 or new_speaker != current_speaker:
                    startTime = srt_format_timestamp(segment['start'])
                    segmentId = idx+1

                if len(textsegment) < segment_length and new_speaker == current_speaker:
                    if wordnumber == 1:
                        textsegment = currentword
                    else:
                        textsegment = textsegment + ' ' + currentword
                    wordnumber = wordnumber + 1
                    if idx+1 == len(speaker_segments):
                        endTime = srt_format_timestamp(segment['end'])
                        srt_segment = f"{segmentId}\n{startTime} --> {endTime}\n{textsegment}\n\n"
                        srtFile.write(srt_segment)
                    else:
                        nextSegment = speaker_segments[idx+1]
                        timeBetweenWords = nextSegment['start'] - segment['end']
                        if timeBetweenWords > 0.5:
                            endTime = srt_format_timestamp(segment['end'])
                            srt_segment = f"{segmentId}\n{startTime} --> {endTime}\n{textsegment}\n\n"
                            srtFile.write(srt_segment)
                            textsegment = ''
                            wordnumber = 1
                else:
                    endTime = srt_format_timestamp(segment['end'])
                    srt_segment = f"{segmentId}\n{startTime} --> {endTime}\n{textsegment + ' ' + currentword}\n\n"
                    srtFile.write(srt_segment)
                    textsegment = ''
                    wordnumber = 1

                current_speaker = new_speaker

        # with open(srt_filename, 'w', encoding='utf-8') as srtFile:
        #     textsegment = ''
        #     wordnumber = 1
        #     for idx, segment in enumerate(speaker_segments):
        #         currentword = segment['word']
        #         if len(textsegment) == 0:
        #             startTime = srt_format_timestamp(segment['start'])
        #             segmentId = idx+1
        #         if len(textsegment) < segment_length:
        #             if wordnumber == 1:
        #                 textsegment = currentword
        #             else:
        #                 textsegment = textsegment + ' ' + currentword
        #             wordnumber = wordnumber + 1
        #             if idx+1 == len(speaker_segments):
        #                 endTime = srt_format_timestamp(segment['end'])
        #                 srt_segment = f"{segmentId}\n{startTime} --> {endTime}\n{textsegment}\n\n"
        #                 srtFile.write(srt_segment)
        #             else:
        #                 nextSegment = speaker_segments[idx+1]
        #                 timeBetweenWords = nextSegment['start'] - segment['end']
        #                 if timeBetweenWords > 0.5:
        #                     endTime = srt_format_timestamp(segment['end'])
        #                     srt_segment = f"{segmentId}\n{startTime} --> {endTime}\n{textsegment}\n\n"
        #                     srtFile.write(srt_segment)
        #                     textsegment = ''
        #                     wordnumber = 1
        #         else:
        #             endTime = srt_format_timestamp(segment['end'])
        #             srt_segment = f"{segmentId}\n{startTime} --> {endTime}\n{textsegment + ' ' + currentword}\n\n"
        #             srtFile.write(srt_segment)
        #             textsegment = ''
        #             wordnumber = 1

    second_speaker_color = clip_info.get('secondSpeakerColor', 'yellow')
    third_speaker_color = clip_info.get('thirdSpeakerColor', 'blue')
    fourth_speaker_color = clip_info.get('fourthSpeakerColor', 'green')
    fifth_speaker_color = clip_info.get('fifthSpeakerColor', 'red')
    speaker_colors = {
        'SPEAKER_00': subtitle_color,
        'SPEAKER_01': second_speaker_color,
        'SPEAKER_02': third_speaker_color,
        'SPEAKER_03': fourth_speaker_color,
        'SPEAKER_04': fifth_speaker_color,
        'SPEAKER_05': 'pink',
    }
    clips = [video]
    for speaker in speakers.keys():
        srt_filename = f"{speaker}.srt"
        color = speaker_colors.get(speaker, 'white')  # default color is white if speaker not found in speaker_colors
        if os.path.exists(srt_filename):
            clip = create_subtitle_clip(srt_filename, color, font, font_size, background_color, font_stroke_width, font_stroke_color, position_horizontal, position_vertical, video)
            clips.append(clip)
        else:
            print(f"Warning: SRT file not found for speaker: {speaker}")

    video_with_subtitles = CompositeVideoClip(clips)
    return video_with_subtitles