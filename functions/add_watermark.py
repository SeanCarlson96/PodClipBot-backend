# from moviepy.editor import ImageClip, CompositeVideoClip

# def add_watermark(video, clip_info):

#     # Choose the watermark image based on conditions
#     if clip_info.get('watermarkToggle') == 'on':
#         watermark_path = "watermarks/PCB_3.png"
#     elif clip_info.get('subscription') == 'none':
#         watermark_path = "watermarks/PCB_fv_1.png"
#     else:
#         video = CompositeVideoClip([video])
#         return video
    

#     position_horizontal = clip_info.get('watermarkPositionHorizontal', 'center').lower()

#     position_percent_vertical = int(clip_info.get('watermarkPositionVertical', '25'))
#     position_vertical = ((100 - position_percent_vertical)) / 100
#     custom_upload = clip_info.get('watermark_file_path', None)
#     height = int(clip_info.get('watermarkSize', '200'))
#     opacity_percent = int(clip_info.get('watermarkOpacity', '100'))
#     opacity = opacity_percent / 100
#     duration = int(clip_info.get('watermarkDuration', '100'))

#     if custom_upload:
#         watermark_path = custom_upload

#     # Add the watermark image overlay
#     watermark = ImageClip(watermark_path)
#     watermark = watermark.set_opacity(opacity).resize(height=height)

#     # watermark = watermark.set_pos(lambda t: ('center', video.size[1] * 0.75 - watermark.size[1] / 2))
#     watermark = watermark.set_position((position_horizontal, position_vertical), relative=True)
#     video = CompositeVideoClip([video, watermark.set_duration(video.duration * (duration / 100.0))])

#     return video


from moviepy.editor import ImageClip, CompositeVideoClip

def add_watermark(video, clip_info):
    # Choose the watermark image based on conditions
    if clip_info.get('watermarkToggle') == 'on':
        watermark_path = "watermarks/PCB_3.png"
        size_divider = 5000
    elif clip_info.get('subscription') == 'none':
        # watermark_path = "watermarks/PCB_fv_4.png"
        watermark_path = "watermarks/PCB_d_1.png"
        size_divider = 3500
    else:
        video = CompositeVideoClip([video])
        return video
    
    position_horizontal = clip_info.get('watermarkPositionHorizontal', 'center').lower()
    position_percent_vertical = int(clip_info.get('watermarkPositionVertical', '25'))
    position_vertical = ((100 - position_percent_vertical)) / 100
    custom_upload = clip_info.get('watermark_file_path', None)
    height_ratio = int(clip_info.get('watermarkSize', '300')) / size_divider # Calculate watermark size ratio
    opacity_percent = int(clip_info.get('watermarkOpacity', '100'))
    opacity = opacity_percent / 100
    duration = int(clip_info.get('watermarkDuration', '100'))

    if custom_upload:
        watermark_path = custom_upload

    # Add the watermark image overlay
    watermark = ImageClip(watermark_path)
    watermark = watermark.set_opacity(opacity).resize(height=int(video.h * height_ratio))  # Set watermark height proportional to video height

    watermark = watermark.set_position((position_horizontal, position_vertical), relative=True)
    video = CompositeVideoClip([video, watermark.set_duration(video.duration * (duration / 100.0))])

    return video
