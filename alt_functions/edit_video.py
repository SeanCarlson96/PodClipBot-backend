from moviepy.editor import *

from functions.center_and_crop import center_and_crop
from alt_functions.whisperx_to_subtitles import add_subtitles
from functions.add_background_music import add_background_music
from functions.add_watermark import add_watermark
import os


def edit_video(temp_file, start_time, end_time, clip_number):

    print('start: ' + str(start_time))
    print('end: ' + str(end_time))
    # print('video: ' + str(video_file))
    print('clip number: ' + str(clip_number))

    # Save the video file to a temporary location to ensure readability
    # temp_file = 'temp.mp4'
    # video_file.save(temp_file)

    # Trim the video using MoviePy
    video = VideoFileClip(temp_file)
    video = video.subclip(start_time, end_time)

    # Center and crop to 9:16
    video = center_and_crop(video)

    # Use whisperx to create subtitles, and add them to the video
    video = add_subtitles(video)

    # Add watermark image overlay
    video = add_watermark(video)

    # Add background music
    video = add_background_music(video)

    # Write edited video to the file name
    trimmed_file = 'clip' + clip_number + '.mp4'
    video.write_videofile(os.path.join('uploads', trimmed_file), codec='libx264', audio_codec='aac')

    # Return the trimmed video file as a response
    return trimmed_file