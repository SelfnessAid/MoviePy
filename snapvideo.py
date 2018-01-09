import imageio
imageio.plugins.ffmpeg.download()
from moviepy.editor import *

video = VideoFileClip("./resources/videos/origin/video1.mp4").subclip(50,60)

# Make the text. Many more options are available.
txt_clip = ( TextClip("snapjerk.com",fontsize=30,color='yellow')
            .set_position(('right', 'bottom'))
            .margin( bottom=20, right=20, opacity=0)
            .set_duration(10) )

image_clip = ( ImageClip("./resources/images/logo.jpg")
               .set_position(('right', 'top'))
               .resize(0.1)
               .set_duration(10))

result = CompositeVideoClip([video, txt_clip, image_clip]) # Overlay text on video
result.write_videofile("./resources/videos/result/video1_result_1.mp4",fps=25) # Many options...