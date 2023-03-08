import cv2
from flask import jsonify
from moviepy.editor import *
from find_faces import find_face_center
import sys

def center_and_crop(video):
    # Crop the video to a 9:16 aspect ratio and 1920x1080 resolution
    target_width = 1080*9//16
    # if video.w/video.h > target_width/1080:
    #     new_width = int(target_width)
    #     new_height = int(video.h * target_width / video.w)
    # else:
    #     new_width = int(video.w * 1080 / video.h)
    #     new_height = 1080
    # x1 = (new_width - target_width) // 2
    x1 = (video.w // 2) - (target_width // 2)
    x2 = x1 + target_width
    y1 = 0
    y2 = 1080
    video = video.crop(x1=x1, y1=y1, x2=x2, y2=y2)
    video = video.resize(width=1920)
    return video


# code below was final try before giving up on centering around faces

    # # Find faces and crop around them
    # face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # # Define the target aspect ratio
    # target_ratio = 9/16

    # # Define the output size
    # output_width = 1920
    # output_height = int(output_width * target_ratio)

    # # Define an empty list to store the cropped frames
    # cropped_frames = []

    # # Calculate the total number of frames in the video (progress bar)
    # total_frames = int(video.duration * video.fps)
    # progress_bar_width = 40


    # # Loop through the frames in the video
    # # for frame in video.iter_frames():
    # for i, frame in enumerate(video.iter_frames()):
    #     # Update the progress bar
    #     percent_done = (i + 1) / total_frames
    #     num_chars = int(percent_done * progress_bar_width)
    #     progress_bar = '[' + '#' * num_chars + ' ' * (progress_bar_width - num_chars) + ']'
    #     sys.stdout.write(f'\rProcessing frame {i + 1}/{total_frames} {progress_bar} {percent_done:.1%}')
    #     sys.stdout.flush()

    #     # Find the center of the face in the frame
    #     center = find_face_center(frame, face_cascade)

    #     # If a face is found, crop the frame
    #     if center is not None:
    #         # Calculate the dimensions of the cropping area
    #         radius = min(frame.shape[0], frame.shape[1]) / 2
    #         width = int(radius * 2 * target_ratio)
    #         height = int(radius * 2)

    #         # Calculate the top-left corner of the cropping area
    #         x = int(center[0] - width/2)
    #         y = int(center[1] - height/2)

    #         # Check that the width and height are greater than 0
    #         if width > 0 and height > 0:
    #             # Crop the frame
    #             cropped_frame = frame[y:y+height, x:x+width]

    #             # Resize the cropped frame
    #             # resized_frame = cv2.resize(cropped_frame, (output_width, output_height))

    #             # Add the resized frame to the list of cropped frames
    #             cropped_frames.append(cropped_frame)

    # # Release the video
    # video.reader.close()

    # # Convert the list of frames to a modified video and return it
    # modified_video = VideoFileClip(video).set_audio(video.audio)
    # modified_video = modified_video.set_duration(video.duration)
    # modified_video = modified_video.set_fps(video.fps)
    # modified_video = modified_video.set_size((output_width, output_height))

    # for frame in cropped_frames:
    #     modified_video = modified_video.append_frames(frame)

    # return modified_video
