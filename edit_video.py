from moviepy.editor import *

from center_and_crop import center_and_crop
from whisperx_to_subtitles import add_subtitles
from add_background_music import add_background_music
from add_watermark import add_watermark

def edit_video(video_file, start_time, end_time):

    print('start: ' + str(start_time))
    print('end: ' + str(end_time))
    
    # Save the video file to a temporary location to ensure readability
    temp_file = 'temp.mp4'
    video_file.save(temp_file)

    # Trim the video using MoviePy
    video = VideoFileClip(temp_file)
    video = video.subclip(start_time, end_time)

    # Center and crop to 9:16
    video = center_and_crop(video)

    # Use speech recognition to create subtitles, and add them to the video
    video = add_subtitles(video)

    # Add watermark image overlay
    video = add_watermark(video)

    # Add background music
    video = add_background_music(video)

    # Write edited video to the file name
    trimmed_file = 'trimmed.mp4'
    video.write_videofile(os.path.join('uploads', trimmed_file))

    # Return the trimmed video file as a response
    return trimmed_file
