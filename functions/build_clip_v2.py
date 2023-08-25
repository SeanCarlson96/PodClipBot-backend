import os
import simplejson as json
from moviepy.editor import *
import uuid
from werkzeug.datastructures import FileStorage

from functions.create_presigned_url import retreive_video_file, upload_video_file
from functions.center_and_crop import center_and_crop
from file_security_functions.safe_video_file import safe_video_file
from functions.add_subtitles import add_subtitles

TMPDIR = "/tmp"

def lambda_handler():
    """
    Process clip for a video

    Input:
        video-file-name: str s3 URL of file
        clip-id: str 
        clip-info: dict
        start-time: str
        end-time: str
        music-file: optional str s3 URL of file
        watermark-file: optional str s3 URL of file
    """
    payload = json.loads(os.environ.get("INPUT_PAYLOAD", "{}"))
    print(payload)

    downloaded_video_file_path = retreive_video_file(payload["video-file-name"], TMPDIR)
    print(downloaded_video_file_path)
    if not downloaded_video_file_path:
        return {'statusCode': 400, 'body': {'success': False}}

    with open(downloaded_video_file_path, 'rb') as fp:
        video_file = FileStorage(fp, filename=downloaded_video_file_path)

        is_safe, message = safe_video_file(video_file, 5000)  # 5000 is the maximum allowed file size in megabytes
        if not is_safe:
            print("video is not safe")
            return {'statusCode': 400, 'body': {'success': False, 'message': message}}

    music_file = payload.get('clip-info', {}).get('music-file')
    #music_temp_file = os.path.join(TMPDIR, 'temp_music.mp3')
    #music_file.save(music_temp_file)

    watermark_file = payload.get('clip-info', {}).get('watermark-file')
    #watermark_temp_file = os.path.join(TMPDIR, 'temp_watermark.png')
    #watermark_file.save(watermark_temp_file)
            
    #if music_file:
    #    is_safe, message = safe_music_file(music_file, 200)
    #    if not is_safe:
    #        return jsonify({'success': False, 'message': message})

        
    #if watermark_file:
    #    is_safe, message = safe_watermark_file(watermark_file, 20)
    #    if not is_safe:
    #        return jsonify({'success': False, 'message': message})

    success = build_clip(
        downloaded_video_file_path, 
        payload["start-time"], 
        payload["end-time"], 
        payload["clip-id"],
        payload["clip-info"]
    )
    return success


def convert_to_seconds(timestamp):
    hours, minutes, seconds = map(int, timestamp.split(':'))
    return hours * 3600 + minutes * 60 + seconds


def build_clip(
    video_file: str, 
    start_time: str, 
    end_time: str, 
    clip_id: str,
    clip_info: dict
):
    # Trim the video using MoviePy
    video = VideoFileClip(video_file)
    start_time = convert_to_seconds(start_time)
    end_time = convert_to_seconds(end_time)
    video = video.subclip(start_time, end_time)

    # Center and crop to 9:16
    video = center_and_crop(video)

    print(start_time, end_time)

    # Extract the audio from the video
    print("extracting audio")
    audio = video.audio
    audio_filename = os.path.join(TMPDIR, os.path.splitext(video.filename)[0] + '.wav')
    audio.write_audiofile(audio_filename)

    if clip_info.get("subtitlesToggle"):
        # Use whisperx to create subtitles, and add them to the video
        print("adding subtitles")
        video = add_subtitles(TMPDIR, video, audio_filename, clip_info)
    
    #TODO
    # Add watermark image overlay, send clip_info for logic inside function
    #video = add_watermark(video, clip_info)

    #TODO
    #if clip_info.get('musicToggle') == 'on':
    #    # Add background music
    #    video = add_background_music(TMPDIR, video, clip_info)


    # Write edited video to the file name
    unique_id = uuid.uuid4()
    # Write edited video to the file name
    trimmed_file = f'clip{clip_id}_{unique_id}.mp4'
    
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
        #TODO: might need to delete the original file first?

        # Write video file with adjusted settings
        video.write_videofile(
            os.path.join(TMPDIR, trimmed_file),
            codec='libx264',
            audio_codec='aac',
            bitrate=bitrate,
            fps=original_fps,
            preset='veryfast',  # Adjust this as needed
            threads=4,  # Adjust this based on how many CPU cores you want to use
            ffmpeg_params=["-profile:v", "high", "-level:v", h264_level, "-pix_fmt", "yuv420p"]
        )

        #upload clip to S3
        upload_video_file(trimmed_file, os.path.splitext(video.filename)[0] + "/")

    except Exception as e:
        print(e)
        return False

    return True

if __name__ == "__main__":
    lambda_handler()
