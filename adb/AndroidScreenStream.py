

__author__ = 'Sekar Madhiyazhagan'


import os
import signal
import subprocess
import sys
import threading
import time

cancelled = False


def __signal_handler(signum, frame):
    global cancelled
    cancelled = True
    return


def __wait(p):
    while (p.poll() == None):
        time.sleep(1)


def __record(n, t, files):
    filename = "/sdcard/screen-recording-" + str(n) + ".mp4"

    __wait(subprocess.Popen(["adb", "shell", "screenrecord", "--size", "1280x720", "--time-limit", str(t), filename]))

    def __complete(files, filename):
        __wait(subprocess.Popen(["adb", "pull", filename]))
        __wait(subprocess.Popen(["adb", "shell", "rm", filename]))

        files.append(os.path.basename(filename))
        return

    threading.Thread(target=__complete, args=(files, filename)).start()
    return


def record(output, t=-1, time_limit=180):
    global cancelled

    n = 0
    files = []

    while ((not cancelled) and ((t == -1) or (t > 0))):
        if ((t > 0) and (t < time_limit)):
            __record(n, t, files)

            t = 0
        elif ((t >= time_limit) or (t < 0)):
            __record(n, time_limit, files)

            if (t > time_limit):
                t = t - time_limit
            elif (t > 0):
                t = 0
        else:
            break

        n = n + 1

    while (len(files) < n):
        time.sleep(1)

    if (len(files) > 0):
        listfile = open(".temp-list.txt", "w")

        for filename in files:
            listfile.write("file '" + filename + "'\n")

        listfile.close()

        __wait(subprocess.Popen(["ffmpeg", "-f", "concat", "-i", ".temp-list.txt", "-c", "copy", output]))

        os.remove(".temp-list.txt")

        for filename in files:
            os.remove(filename)

    return


if (len(sys.argv) > 1):
    signal.signal(signal.SIGINT, __signal_handler)

    __wait(subprocess.Popen(["adb", "start-server"]))

    if (len(sys.argv) > 2):
        record(sys.argv[1], int(sys.argv[2]))
    else:
        record(sys.argv[1])

    __wait(subprocess.Popen(["adb", "kill-server"]))
else:
    print("Please enter a filename for recording...")
