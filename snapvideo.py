import imageio
imageio.plugins.ffmpeg.download()
from moviepy.editor import *
from multiprocessing import Process, Semaphore
import os
from os import listdir
from os.path import isfile, join
import sys
import threading
import random
import shutil

pool_sema = Semaphore(6)
processes = []
index = 0

#############################
# Check if file is video file.
#############################
def is_VideoFile(filename):
    videoFile_extensions = (
        '.264', '.3g2', '.3gp', '.3gp2', '.3gpp', '.3gpp2', '.3mm', '.3p2', '.60d', '.787', '.89', '.aaf', '.aec', '.aep', '.aepx',
        '.aet', '.aetx', '.ajp', '.ale', '.am', '.amc', '.amv', '.amx', '.anim', '.aqt', '.arcut', '.arf', '.asf', '.asx', '.avb',
        '.avc', '.avd', '.avi', '.avp', '.avs', '.avs', '.avv', '.axm', '.bdm', '.bdmv', '.bdt2', '.bdt3', '.bik', '.bin', '.bix',
        '.bmk', '.bnp', '.box', '.bs4', '.bsf', '.bvr', '.byu', '.camproj', '.camrec', '.camv', '.ced', '.cel', '.cine', '.cip',
        '.clpi', '.cmmp', '.cmmtpl', '.cmproj', '.cmrec', '.cpi', '.cst', '.cvc', '.cx3', '.d2v', '.d3v', '.dat', '.dav', '.dce',
        '.dck', '.dcr', '.dcr', '.ddat', '.dif', '.dir', '.divx', '.dlx', '.dmb', '.dmsd', '.dmsd3d', '.dmsm', '.dmsm3d', '.dmss',
        '.dmx', '.dnc', '.dpa', '.dpg', '.dream', '.dsy', '.dv', '.dv-avi', '.dv4', '.dvdmedia', '.dvr', '.dvr-ms', '.dvx', '.dxr',
        '.dzm', '.dzp', '.dzt', '.edl', '.evo', '.eye', '.ezt', '.f4p', '.f4v', '.fbr', '.fbr', '.fbz', '.fcp', '.fcproject',
        '.ffd', '.flc', '.flh', '.fli', '.flv', '.flx', '.gfp', '.gl', '.gom', '.grasp', '.gts', '.gvi', '.gvp', '.h264', '.hdmov',
        '.hkm', '.ifo', '.imovieproj', '.imovieproject', '.ircp', '.irf', '.ism', '.ismc', '.ismv', '.iva', '.ivf', '.ivr', '.ivs',
        '.izz', '.izzy', '.jss', '.jts', '.jtv', '.k3g', '.kmv', '.ktn', '.lrec', '.lsf', '.lsx', '.m15', '.m1pg', '.m1v', '.m21',
        '.m21', '.m2a', '.m2p', '.m2t', '.m2ts', '.m2v', '.m4e', '.m4u', '.m4v', '.m75', '.mani', '.meta', '.mgv', '.mj2', '.mjp',
        '.mjpg', '.mk3d', '.mkv', '.mmv', '.mnv', '.mob', '.mod', '.modd', '.moff', '.moi', '.moov', '.mov', '.movie', '.mp21',
        '.mp21', '.mp2v', '.mp4', '.mp4v', '.mpe', '.mpeg', '.mpeg1', '.mpeg4', '.mpf', '.mpg', '.mpg2', '.mpgindex', '.mpl',
        '.mpl', '.mpls', '.mpsub', '.mpv', '.mpv2', '.mqv', '.msdvd', '.mse', '.msh', '.mswmm', '.mts', '.mtv', '.mvb', '.mvc',
        '.mvd', '.mve', '.mvex', '.mvp', '.mvp', '.mvy', '.mxf', '.mxv', '.mys', '.ncor', '.nsv', '.nut', '.nuv', '.nvc', '.ogm',
        '.ogv', '.ogx', '.osp', '.otrkey', '.pac', '.par', '.pds', '.pgi', '.photoshow', '.piv', '.pjs', '.playlist', '.plproj',
        '.pmf', '.pmv', '.pns', '.ppj', '.prel', '.pro', '.prproj', '.prtl', '.psb', '.psh', '.pssd', '.pva', '.pvr', '.pxv',
        '.qt', '.qtch', '.qtindex', '.qtl', '.qtm', '.qtz', '.r3d', '.rcd', '.rcproject', '.rdb', '.rec', '.rm', '.rmd', '.rmd',
        '.rmp', '.rms', '.rmv', '.rmvb', '.roq', '.rp', '.rsx', '.rts', '.rts', '.rum', '.rv', '.rvid', '.rvl', '.sbk', '.sbt',
        '.scc', '.scm', '.scm', '.scn', '.screenflow', '.sec', '.sedprj', '.seq', '.sfd', '.sfvidcap', '.siv', '.smi', '.smi',
        '.smil', '.smk', '.sml', '.smv', '.spl', '.sqz', '.srt', '.ssf', '.ssm', '.stl', '.str', '.stx', '.svi', '.swf', '.swi',
        '.swt', '.tda3mt', '.tdx', '.thp', '.tivo', '.tix', '.tod', '.tp', '.tp0', '.tpd', '.tpr', '.trp', '.ts', '.tsp', '.ttxt',
        '.tvs', '.usf', '.usm', '.vc1', '.vcpf', '.vcr', '.vcv', '.vdo', '.vdr', '.vdx', '.veg','.vem', '.vep', '.vf', '.vft',
        '.vfw', '.vfz', '.vgz', '.vid', '.video', '.viewlet', '.viv', '.vivo', '.vlab', '.vob', '.vp3', '.vp6', '.vp7', '.vpj',
        '.vro', '.vs4', '.vse', '.vsp', '.w32', '.wcp', '.webm', '.wlmp', '.wm', '.wmd', '.wmmp', '.wmv', '.wmx', '.wot', '.wp3',
        '.wpl', '.wtv', '.wve', '.wvx', '.xej', '.xel', '.xesc', '.xfl', '.xlmv', '.xmv', '.xvid', '.y4m', '.yog', '.yuv', '.zeg',
        '.zm1', '.zm2', '.zm3', '.zmv')

    if filename.endswith((videoFile_extensions)):
        return True

    return False


def split_videofile(filename, clip_start, clip_end, num):
    try:
        video = VideoFileClip("./resources/videos/origin/" + filename).subclip(clip_start, clip_end).resize((640, 360))
        result = CompositeVideoClip([video])
        filename, file_extension = os.path.splitext(filename)
        result.write_videofile("./resources/videos/origin/" + filename + "_split_" + str(num) + file_extension, fps=25, threads=1)
    except IOError as e:
        print(e.strerror)
    finally:
        pool_sema.release()


def is_alive_anyProcess():
    for process in processes:
        if process.is_alive():
            return True

    return False

def split_videos():
    global processes
    intervals = [15, 30, 60, 120]
    for root, dirs, files in os.walk("./resources/videos/origin"):
        for filename in files:
            if not is_VideoFile(filename):
                continue

            video = VideoFileClip("./resources/videos/origin/" + filename)
            duration = video.duration

            clip_start = 0
            num = 1

            while clip_start < duration:
                interval = random.choice(intervals)
                clip_end = clip_start + interval
                if clip_end > duration:
                    clip_end = duration
                pool_sema.acquire()
                p = Process(target=split_videofile, args=(filename, clip_start, clip_end, num))
                p.start()
                processes.append(p)
                clip_start = clip_end
                num += 1

            index = 0
            while is_alive_anyProcess():
                index = (index + 1) % 2
            os.remove("./resources/videos/origin/" + filename)


def complinate_video():
    global index
    files = [f for f in listdir("./resources/videos/complinations") if isfile(join("./resources/videos/complinations", f))]
    files.remove(".DS_Store")
    clips = []
    duration = 0
    for filename in files:
        clip = VideoFileClip("./resources/videos/complinations/" + filename)
        duration =  duration + clip.duration
        clips.append(clip)

    video = concatenate_videoclips(clips)


    txt_clip = ( TextClip("snapjerk.com",fontsize=30,color='yellow')
                .set_position(('right', 'bottom'))
                .margin( bottom=20, right=20, opacity=0)
                .set_duration(duration) )

    image_clip = ( ImageClip("./resources/images/logo.jpg")
                .set_position(('right', 'top'))
                .resize(0.1)
                .set_duration(duration))

    result = CompositeVideoClip([video, txt_clip, image_clip])
    result.write_videofile("./resources/videos/result/snapvideo_" + str(index) + ".mp4", fps=25)
    index = index + 1

    for clip in clips:
        del clip.reader

    for filename in files:
        os.remove("./resources/videos/complinations/" + filename)


def complinate_videos():
    files = [f for f in listdir("./resources/videos/origin") if isfile(join("./resources/videos/origin", f))]
    while True:
        if not files:
            break

        total_time = 0
        
        while True:
            selected_file = random.choice(files)
        
            if selected_file == ".DS_Store":
                files.remove(selected_file)
                continue
        
            video = VideoFileClip("./resources/videos/origin/" + selected_file)
            total_time = total_time + video.duration
        
            if total_time > 720:
                break
        
            shutil.copy2("./resources/videos/origin/" + selected_file, "./resources/videos/complinations")
            files.remove(selected_file)
            os.remove("./resources/videos/origin/" + selected_file)
        
            if not files:
                break

        complinate_video()

        
def process_videos():
    # split_videos()
    complinate_videos()


def main():
    process_videos()


if __name__ == '__main__':
    main()