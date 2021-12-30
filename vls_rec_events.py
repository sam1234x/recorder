# USAGE
# python save_key_events.py --output output

# import the necessary packages
from pyimagesearch.keyclipwriter import KeyClipWriter
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
    help="path to output directory")
ap.add_argument("-p", "--picamera", type=int, default=-1,
    help="whether or not the Raspberry Pi camera should be used")
ap.add_argument("-f", "--fps", type=int, default=15,
    help="FPS of output video")
ap.add_argument("-c", "--codec", type=str, default="MJPG",
    help="codec of output video")
ap.add_argument("-b", "--buffer-size", type=int, default=32,
    help="buffer size of video clip writer")
args = vars(ap.parse_args())

# Open the log file
sourceFile = open('/home/pi/VLSData/vls_log.txt', 'a')

# initialize the video stream and allow the camera sensor to
# warmup
timestamp = datetime.datetime.now()
print(timestamp.strftime("%Y%m%d-%H%M%S"),":[INFO] warming up camera...",file = sourceFile)

vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
time.sleep(2.0)

# initialize key clip writer and the consecutive number of
# frames that have *not* contained any action
kcw = KeyClipWriter(bufSize=args["buffer_size"])
consecFrames = 0
recStart = 1

# keep looping
while True:
    # grab the current frame, resize it, and initialize a
    # boolean used to indicate if the consecutive frames
    # counter should be updated
    frame = vs.read()
    updateConsecFrames = True
    
        
    # blur the frame and convert it to the HSV color space
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    

    temp = cv2.sumElems(frame);
    start_flag = temp[0] + temp[1] + temp[2];
    #start_flag = 12
    
    # only proceed if start_flag is not equal to 126974425
    if start_flag != 126974425:
        
        if recStart == 1:
           timestamp = datetime.datetime.now()
           print(timestamp.strftime("%Y%m%d-%H%M%S"),":[STATUS] Recording...",file = sourceFile)
           sourceFile.close()
           sourceFile = open('/home/pi/VLSData/vls_log.txt', 'a')
           recStart = 0

        # if we are not already recording, start recording
        if not kcw.recording:
            timestamp = datetime.datetime.now()
            p = "{}/{}.avi".format(args["output"],
                timestamp.strftime("%Y%m%d-%H%M%S"))
            kcw.start(p, cv2.VideoWriter_fourcc(*args["codec"]),
                args["fps"])

    # otherwise, no action has taken place in this frame, so
    # increment the number of consecutive frames that contain
    # no action
    if updateConsecFrames:
        consecFrames += 1

    # update the key frame clip buffer
    kcw.update(frame)

    # if we are recording and reached a threshold on consecutive
    # number of frames with no action, stop recording the clip
    if kcw.recording and start_flag == 126974425:
       #print("Correct Flag")
       kcw.finish()
       recStart = True
       timestamp = datetime.datetime.now()
       print(timestamp.strftime("%Y%m%d-%H%M%S"),":[STATUS] Finished Recording...",file = sourceFile)
       timestamp = datetime.datetime.now()
       print(timestamp.strftime("%Y%m%d-%H%M%S"),":[STATUS] Closing File.",file = sourceFile)
       sourceFile.close()
       sourceFile = open('/home/pi/VLSData/vls_log.txt', 'a')

    # show the frame
    #cv2.imshow("Frame", frame)
    #key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    #if key == ord("q"):
    #    break

# if we are in the middle of recording a clip, wrap it up
if kcw.recording:
    kcw.finish()
    recStart = True
    print(timestamp.strftime("%Y%m%d-%H%M%S"),":[STATUS] Ending Recording...",file = sourceFile)
    timestamp = datetime.datetime.now()
    print(timestamp.strftime("%Y%m%d-%H%M%S"),":[STATUS] Closing File.",file = sourceFile)
    sourceFile.close()
    sourceFile = open('/home/pi/VLSData/vls_log.txt', 'a')

#do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

timestamp = datetime.datetime.now()
print(timestamp.strftime("%Y%m%d-%H%M%S"),":[INFO] Program Succesfully Closed ...",file = sourceFile)
sourceFile.close()
