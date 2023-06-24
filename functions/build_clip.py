from pprint import pprint
from moviepy.editor import *

from functions.center_and_crop import center_and_crop
# from whisperx_to_subtitles import add_subtitles
from functions.add_subtitles import add_subtitles, send_progress_update
from functions.add_background_music import add_background_music
from functions.add_watermark import add_watermark
import os
from functions.custom_logger import CancelProcessingException, MyBarLogger
import uuid
# from flask_socketio import SocketIO
# from application import socketio

__all__ = ['clip_cancel_flags']

clip_cancel_flags = {}

def convert_to_seconds(timestamp):
    hours, minutes, seconds = map(int, timestamp.split(':'))
    return hours * 3600 + minutes * 60 + seconds

def check_for_cancel(clip_name, socketio, socket_id):
    global clip_cancel_flags
    if clip_cancel_flags.get(clip_name):
        socketio.emit('processing_canceled', {'clipName': clip_name}, room=socket_id)
        # clip_cancel_flags.pop(clip_name)
        print("clip was canceled, process should exit")
        return True
    return False

def cancel_processing(clip_name, socketio_instance, socket_id):
    print(clip_name + ' canceled')
    global clip_cancel_flags
    clip_cancel_flags[clip_name] = True
    socketio_instance.emit('processing_canceled', {'clipName': clip_name}, room=socket_id)

def build_clip(tempdir, temp_file, start_time, end_time, clip_number, socketio, clip_info, socket_id):
    print(clip_cancel_flags)

    
    clip_name = "Clip " + str(clip_number)
    if check_for_cancel(clip_name, socketio, socket_id):
        return
    
    socketio.emit('current_clip_in_edit', {'name': clip_name}, room=socket_id)

    # Trim the video using MoviePy
    video = VideoFileClip(temp_file)
    start_time = convert_to_seconds(start_time)
    end_time = convert_to_seconds(end_time)
    video = video.subclip(start_time, end_time)
    if check_for_cancel(clip_name, socketio, socket_id):
        return
    # Center and crop to 9:16
    video = center_and_crop(video)
    if check_for_cancel(clip_name, socketio, socket_id):
        return
    print(start_time, end_time)
    # pprint(clip_info)

    # Extract the audio from the video
    audio = video.audio
    # audio_filename = os.path.splitext(video.filename)[0] + '.wav'
    audio_filename = os.path.join(tempdir, os.path.splitext(video.filename)[0] + '.wav')
    audio.write_audiofile(audio_filename)

    if clip_info.get('subtitlesToggle') == 'on':
        # Use whisperx to create subtitles, and add them to the video
        video = add_subtitles(tempdir, video, audio_filename, clip_info, socketio, socket_id)
        if check_for_cancel(clip_name, socketio, socket_id):
            return

    
    # Add watermark image overlay, send clip_info for logic inside function
    video = add_watermark(video, clip_info)
    if check_for_cancel(clip_name, socketio, socket_id):
        return


    if clip_info.get('musicToggle') == 'on':
        # Add background music
        video = add_background_music(tempdir, video, clip_info)
        if check_for_cancel(clip_name, socketio, socket_id):
            return


    # Write edited video to the file name
    # trimmed_file = 'clip' + clip_number + '.mp4'
    # Generate a unique id
    unique_id = uuid.uuid4()
    # Write edited video to the file name
    trimmed_file = f'clip{clip_number}_{unique_id}.mp4'
    
    my_bar_logger = MyBarLogger(socketio, clip_cancel_flags, clip_name, socket_id)
    socketio.emit('build_action', {'action': 'Writing'}, room=socket_id)
    upload_dir = os.path.join('uploads')
    os.makedirs(upload_dir, exist_ok=True)
    # try:
    #     video.write_videofile(
    #         os.path.join(upload_dir, trimmed_file),
    #         codec='libx264',
    #         audio_codec='aac',
    #         bitrate='8000k',  # This sets the bitrate to 8000 kb/s. Added this to hopefully fix the corruption on upload issue with YouTube. This might need to be a calutaed value based on the 
    #         logger=my_bar_logger
    #     )
    # Get properties of the original video
    original_fps = video.fps or 30  # Fallback to 30 if original frame rate isn't available

    # Determine video resolution
    height = video.size[1]
    if height >= 2160:
        resolution = '4k'
    elif height >= 1440:
        resolution = '2k'
    elif height >= 1080:
        resolution = '1080p'
    elif height >= 720:
        resolution = '720p'
    elif height >= 480:
        resolution = '480p'
    else:
        resolution = '360p'

    # Bitrate calculation based on YouTube recommendations
    if resolution == '4k':
        bitrate = '45000k' if original_fps > 30 else '35000k'
    elif resolution == '2k':
        bitrate = '24000k' if original_fps > 30 else '16000k'
    elif resolution == '1080p':
        bitrate = '12000k' if original_fps > 30 else '8000k'
    elif resolution == '720p':
        bitrate = '7500k' if original_fps > 30 else '5000k'
    elif resolution == '480p':
        bitrate = '2500k'
    else:
        bitrate = '1000k'

    # Calculate appropriate H.264 level based on frame rate
    if original_fps > 30:
        h264_level = '4.2'
    else:
        h264_level = '4.0'

    # Make sure dimensions are divisible by 2
    width, height = video.size
    if width % 2 != 0:
        width -= 1
    if height % 2 != 0:
        height -= 1

    # Resize the video
    video = video.resize((width, height))

    try:
        # Write video file with adjusted settings
        video.write_videofile(
            os.path.join(upload_dir, trimmed_file),
            codec='libx264',
            audio_codec='aac',
            bitrate=bitrate,
            fps=original_fps,
            preset='veryfast',  # Adjust this as needed
            # threads=4,  # Adjust this based on how many CPU cores you want to use
            ffmpeg_params=["-profile:v", "high", "-level:v", h264_level, "-pix_fmt", "yuv420p"],
            logger=my_bar_logger
        )

    except CancelProcessingException as e:
        print(str(e))
        socketio.emit('processing_canceled', {'clipName': clip_name}, room=socket_id)
        return
    if check_for_cancel(clip_name, socketio, socket_id):
        return
    socketio.emit('video_file_ready', {'filename': trimmed_file, 'name': clip_name}, room=socket_id)
    print(clip_number + ' emitted')
    return trimmed_file
