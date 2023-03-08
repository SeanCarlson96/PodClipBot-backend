from flask import jsonify
from moviepy.editor import *

def edit_video(video_file, start_time, end_time):
    
    # Save the video file to a temporary location
    temp_file = 'temp.mp4'
    video_file.save(temp_file)

    # Trim the video using MoviePy
    video = VideoFileClip(temp_file)

    # Crop the video to a 16:9 aspect ratio and center on the subject
    # video = video.crop(x1=0.15*video.w, y1=0.15*video.h, x2=0.85*video.w, y2=0.85*video.h)
    # video = video.resize(width=1280)

    # Crop the video to a 9:16 aspect ratio and 1920x1080 resolution
    target_width = 1080*9//16
    if video.w/video.h > target_width/1080:
        new_width = int(target_width)
        new_height = int(video.h * target_width / video.w)
    else:
        new_width = int(video.w * 1080 / video.h)
        new_height = 1080
    x1 = (new_width - target_width) // 2
    x2 = x1 + target_width
    y1 = 0
    y2 = 1080
    video = video.crop(x1=x1, y1=y1, x2=x2, y2=y2)
    video = video.resize(width=1920)

    # Add subtitles
    txt_clip = TextClip("Hello, world!", fontsize=50, color='white')
    txt_clip = txt_clip.set_pos('bottom').set_duration(video.duration)
    video = CompositeVideoClip([video, txt_clip])

    # Add background music
    audio_clip = AudioFileClip("impressionist.mp3")
    audio_clip = audio_clip.set_duration(video.duration)
    video = video.set_audio(audio_clip)

    # Add watermark image overlay
    watermark = ImageClip("SClogoWatermark.png")
    watermark = watermark.set_opacity(0.9).resize(height=50)
    watermark = watermark.set_pos(('right', 'bottom'))
    video = CompositeVideoClip([video, watermark])

    # Trim the video using MoviePy
    trimmed_video = video.subclip(start_time, end_time)
    trimmed_file = 'trimmed.mp4'
    trimmed_video.write_videofile(trimmed_file)

    # Return the trimmed video file as a response
    return jsonify({'success': True, 'file': trimmed_file})
