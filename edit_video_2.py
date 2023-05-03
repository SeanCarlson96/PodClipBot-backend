from moviepy.editor import *

from center_and_crop import center_and_crop
from whisperx_to_subtitles import add_subtitles
from add_background_music import add_background_music
from add_watermark import add_watermark
import os
from custom_logger import CancelProcessingException, MyBarLogger
import socketio

__all__ = ['clip_cancel_flags']

clip_cancel_flags = {}

def edit_video_with_socketio(temp_file, start_time, end_time, clip_number, socketio):

    clip_name = "Clip " + str(clip_number)
    
    print('cancel flags: ' + str(clip_cancel_flags))

    if clip_cancel_flags.get(clip_name):
        socketio.emit('processing_canceled', {'clipName': clip_name})
        return

    print('Editing: ' + clip_name)
    # print('start: ' + str(start_time))
    # print('end: ' + str(end_time))
    # print('video: ' + str(video_file))

    socketio.emit('current_clip_in_edit', {'name': clip_name})

    # Trim the video using MoviePy
    video = VideoFileClip(temp_file)

    video = video.subclip(start_time, end_time)

    if clip_cancel_flags.get(clip_name):
        socketio.emit('processing_canceled', {'clipName': clip_name})
        return

    # Center and crop to 9:16
    video = center_and_crop(video)

    if clip_cancel_flags.get(clip_name):
        socketio.emit('processing_canceled', {'clipName': clip_name})
        return

    # Use whisperx to create subtitles, and add them to the video
    video = add_subtitles(video)

    if clip_cancel_flags.get(clip_name):
        socketio.emit('processing_canceled', {'clipName': clip_name})
        return

    # Add watermark image overlay
    video = add_watermark(video)

    if clip_cancel_flags.get(clip_name):
        socketio.emit('processing_canceled', {'clipName': clip_name})
        return

    # Add background music
    video = add_background_music(video)

    if clip_cancel_flags.get(clip_name):
        socketio.emit('processing_canceled', {'clipName': clip_name})
        return

    # Write edited video to the file name
    trimmed_file = 'clip' + clip_number + '.mp4'
    my_bar_logger = MyBarLogger(socketio, clip_cancel_flags, clip_name)
    # video.write_videofile(
    #     os.path.join('uploads', trimmed_file),
    #     codec='libx264',
    #     audio_codec='aac',
    #     logger=my_bar_logger
    # )
    try:
        video.write_videofile(
            os.path.join('uploads', trimmed_file),
            codec='libx264',
            audio_codec='aac',
            logger=my_bar_logger
        )
    # except CancelProcessingException as e:
    #     print(str(e))
    #     socketio.emit('processing_canceled', {'filename': trimmed_file})
    #     return
    except CancelProcessingException as e:
        print(str(e))
        socketio.emit('processing_canceled', {'clipName': clip_name})
        return


    if clip_cancel_flags.get(clip_name):
        socketio.emit('processing_canceled', {'clipName': clip_name})
        return

    # socketio.emit('video_file_ready', {'filename': trimmed_file, 'name':
    # clip_name'})
    socketio.emit('video_file_ready', {'filename': trimmed_file, 'name': clip_name})

    print(clip_number + ' emitted')
    # Return the trimmed video file as a response
    return trimmed_file


def cancel_processing(clip_name, socketio_instance):
    print(clip_name + ' canceled')
    global clip_cancel_flags
    clip_cancel_flags[clip_name] = True
    socketio_instance.emit('processing_canceled', {'clipName': clip_name})
