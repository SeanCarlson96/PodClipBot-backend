from moviepy.editor import *

from center_and_crop import center_and_crop
from whisperx_to_subtitles import add_subtitles
from add_background_music import add_background_music
from add_watermark import add_watermark
import os
from custom_logger import MyBarLogger
import socketio


def edit_video_with_socketio(temp_file, start_time, end_time, clip_number, socketio):

    print('start: ' + str(start_time))
    print('end: ' + str(end_time))
    # print('video: ' + str(video_file))
    print('clip number: ' + str(clip_number))

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
    my_bar_logger = MyBarLogger(socketio)
    video.write_videofile(
        os.path.join('uploads', trimmed_file),
        codec='libx264',
        audio_codec='aac',
        logger=my_bar_logger
    )
    socketio.emit('video_file_ready', {'filename': trimmed_file})

    # Return the trimmed video file as a response
    return trimmed_file