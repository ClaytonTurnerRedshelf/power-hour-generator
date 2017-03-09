# Adapted from: https://github.com/michaelpippolito/power_hour/blob/master/powerhour.py

import os
import subprocess
import ffmpeg_split

def timeStampConvert(timeStamp):
    minutes = int(timeStamp[0:timeStamp.rfind(":")])
    seconds = int(timeStamp[timeStamp.rfind(":") + 1:])
    return (minutes * 60000) + (seconds * 1000)


def timeStampConvertToSeconds(timeStamp):
    minutes = int(timeStamp[0:timeStamp.rfind(":")])
    seconds = int(timeStamp[timeStamp.rfind(":") + 1:])
    return ((minutes * 60000) + (seconds * 1000)) / 1000


# open power hour text file
song_file = open("songs.txt", "r")

# download beep
print("Downloading beep...")
subprocess.call("youtube-dl --quiet -f mp4 -o beep_full.mp4 "
                + song_file.readline(), shell=True)

# Cut beep video
beepStart = timeStampConvertToSeconds(song_file.readline())
beepEnd = timeStampConvertToSeconds(song_file.readline())
beepLength = beepEnd - beepStart
filename = "beep.csv"
with open(filename, "w+") as csvfile:
    csvfile.write("start_time,length,rename_to\n")
    csvfile.write(str(beepStart) + "," + str(beepLength) + ",beep.mp4")
#ffmpeg_split.split_by_manifest("beep_full.mp4", filename)#, vcodec="h264")
subprocess.call("ffmpeg -ss " + str(beepStart) + " -i beep_full.mp4" +
                        " -t " + str(beepLength) + " -vcodec libx264 -acodec aac -strict experimental -r 24 -async 1 -y beep.mp4")
#subprocess.call("ffmpeg -i beep.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts beep.ts"
subprocess.call("ffmpeg -i beep.mp4 -vf scale=1280:720,setdar=16:9 beep.ts"
                , shell=True)
os.remove("beep_full.mp4")
#os.remove("beep.mp4")
os.remove(filename)

# beep = beep[beepStart:beepEnd]
# save beep
# remove full beep video and rename to what we want

songLength = 60
duration = "01:00"
concat_vid_string = "concat:"
concat_vid_string_mp4 = ""
concat_vid_filter = "ffmpeg "
for i in range(1, 61):
    link = song_file.readline()

    if link:
        curSong = str(i)

        start_time = song_file.readline().strip()
        start = timeStampConvertToSeconds(start_time)

        print("Downloading song " + curSong + " of 60...")
        subprocess.call("youtube-dl --quiet -f mp4 -o " + curSong + "_full.mp4 " + link, shell=True)
        #filename = curSong + ".csv"
        #with open(filename, "w+") as csvfile:
        #    csvfile.write("start_time,length,rename_to\n")
        #    csvfile.write(str(start) + "," + str(songLength) + "," + curSong + ".mp4")
        #ffmpeg_split.split_by_manifest(curSong + "_full.mp4", filename)#, vcodec="h264")
        subprocess.call("ffmpeg " +
                        " -ss " + str(start_time) + " -i " + curSong + "_full.mp4 " +
                        " -t " + duration + " -vcodec libx264 -acodec aac -strict experimental -r 24 -async 1 -y " + curSong + ".mp4")
        os.remove(curSong + "_full.mp4")
        #os.remove(curSong+".csv")

        #subprocess.call("ffmpeg -i " + curSong + ".mp4 -c copy  " + curSong + ".ts"
        subprocess.call("ffmpeg -i " + curSong +".mp4 -vf scale=1280:720,setdar=16:9 " + curSong + ".ts"
                        , shell=True)
        #os.remove(curSong+".mp4")
        concat_vid_string += curSong + ".ts|beep.ts|"
        concat_vid_string_mp4 += "file " + curSong + ".mp4\n"
        concat_vid_filter += "-i " + curSong + ".mp4 "

# Protocol attempt
print(concat_vid_string,concat_vid_string[:-9])
#subprocess.call("ffmpeg -i \"" + concat_vid_string[:-9] + "\"  -c copy -bsf:a aac_adtstoasc powerhour.mp4")
subprocess.call("ffmpeg -i \"" + concat_vid_string[:-9] + "\"  -c copy -s 1280:720 powerhour.mp4")
#subprocess.call("ffmpeg -i \"" + concat_vid_string[:-9] + "\" -vf scale=1280:-1:force_original_aspect_ratio=decrease powerhour.mp4", shell = True)

# Demuxer attempt
##f = open("inputs.txt","w")
##f.write(concat_vid_string_mp4[:-1])
##f.close()
##subprocess.call("ffmpeg -f concat -i inputs.txt -vcodec copy -acodec copy Power_Hour.mp4"
##                , shell=True)
#subprocess.call("ffmpeg -i 1.mp4 -i 2.mp4 -i 3.mp4 -vcodec copy -acodec copy Power_Hour.mp4")

# Filter attempt
#concat_vid_filter += "-vf scale=1280:720:force_original_aspect_ratio=decrease powerhour.mp4"
#subprocess.call(concat_vid_filter, shell=True)

# When debugging, comment this out
for root, dirs, files in os.walk(os.getcwd()):
    for currentFile in files:
        if any(currentFile.lower().endswith(ext) for ext in ["ts"]):
                os.remove(os.path.join(root, currentFile))
