import glob
import os
import pprint
import traceback
import whisperx
import gc 
from moviepy.editor import TextClip
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from functions.srt_format_timestamp import srt_format_timestamp

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

def diarized_subtitles(clip_info, device, audio_file, result_aligned, segment_length, video, font, font_size, subtitle_color, background_color, font_stroke_width, font_stroke_color, position_horizontal, position_vertical):
    second_speaker_color = clip_info.get('secondSpeakerColor', 'yellow')
    hf_token = os.environ["HF_TOKEN"]
    print('hi')
    # 3. Assign speaker labels
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=hf_token, device=device)
    print('2')
    # add min/max number of speakers if known
    diarize_segments = diarize_model(audio_file)
    print('3')
    # diarize_model(audio_file, min_speakers=min_speakers, max_speakers=max_speakers)
    result = whisperx.assign_word_speakers(diarize_segments, result_aligned)

    segments = result['word_segments']

    # Get a list of all .srt files in the current directory
    srt_files = glob.glob('*.srt')

    # Clear the contents of each .srt file
    for srt_filename in srt_files:
        with open(srt_filename, 'w', encoding='utf-8') as srtFile:
            srtFile.write('')

    # Create a dictionary to hold segments for each speaker
    # speakers = {}
    # for segment in segments:
    #     speaker = segment['speaker']
    #     if speaker not in speakers:
    #         speakers[speaker] = []
    #     speakers[speaker].append(segment)
    # Create a dictionary to hold segments for each speaker
    speakers = {}
    for segment in segments:
        # Check if 'speaker' is present in segment
        if 'speaker' in segment:
            speaker = segment['speaker']
            if speaker not in speakers:
                speakers[speaker] = []
            speakers[speaker].append(segment)
        else:
            print(f"Warning: 'speaker' key not found in segment: {segment}")

    print(segments)

    # Now, for each speaker, generate an SRT file
    for speaker, speaker_segments in speakers.items():
        print('speaker')
        # Set a filename for this speaker
        srt_filename = f"{speaker}.srt"

        # Create the file if it doesn't exist
        with open(srt_filename, 'a') as srtFile:
            pass
        
        with open(srt_filename, 'w', encoding='utf-8') as srtFile:
            textsegment = ''
            wordnumber = 1
            for idx, segment in enumerate(speaker_segments):
                currentword = segment['word']
                if len(textsegment) == 0:
                    startTime = srt_format_timestamp(segment['start'])
                    segmentId = idx+1
                if len(textsegment) < segment_length:
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
    
    # Define the colors for the speakers
    speaker_colors = {
        'SPEAKER_00': subtitle_color,
        'SPEAKER_01': second_speaker_color,
        'SPEAKER_02': 'blue',
        'SPEAKER_03': 'green',
        'SPEAKER_04': 'red',
        'SPEAKER_05': 'pink',
    }

    clips = [video]
    print('clips')
    # Loop over each speaker's SRT file
    # for speaker, color in speaker_colors.items():
    #     srt_filename = f"{speaker}.srt"

    #     generator = lambda txt: TextClip(
    #         txt,
    #         font=font,
    #         fontsize=font_size,
    #         color=color,
    #         bg_color=background_color,
    #         stroke_width=font_stroke_width,
    #         stroke_color=font_stroke_color,
    #         method='label',
    #     )

    #     subtitle_clip = SubtitlesClip(srt_filename, generator).set_position((position_horizontal,position_vertical), relative=True)
    #     clips.append(subtitle_clip.set_duration(video.duration))
    # Loop over each speaker's SRT file
    # Loop over each speaker's SRT file
    for speaker, color in speaker_colors.items():
        print('speaker 2')
        srt_filename = f"{speaker}.srt"

        # Check if the SRT file exists before trying to create a subtitle clip
        if os.path.exists(srt_filename):
            print('speaker 3')
            clip = create_subtitle_clip(srt_filename, color, font, font_size, background_color, font_stroke_width, font_stroke_color, position_horizontal, position_vertical, video)
            clips.append(clip)
        else:
            print(f"Warning: SRT file not found for speaker: {speaker}")


    print('speaker 4')
    # Add all the subtitle clips to the video
    print(len(clips))
    video_with_subtitles = CompositeVideoClip(clips)
    print('diarized subtitles complete')

    return video_with_subtitles