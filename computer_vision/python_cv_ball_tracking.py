# Import the necessary packages:
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time


# Construct the argument parser and parse the arguments:
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help = "path to the (optional) video file")
ap.add_argument("-b", "--buffer", type = int, default = 64, help = "max buffer size")
args = vars(ap.parse_args())

# Define the lower and upper boundaries of the "yellow"
# ball in the HSV color space, then initialize the
# list of tracked points

yellowLower = (1, 78, 207)
yellowUpper = (64, 255, 255)
pts = deque(maxlen=args["buffer"])

# If a video path was not supplied, grab the reference
# to the webcam:

if not args.get("video", False):
    vs = VideoStream(src = 0).start()

# otherwise, grab a reference to the video file:
else:
    vs = cv2.VideoCapture(args["video"])
    
# Allow the camera or video file to warm up
time.sleep(2.0)

# Variables for game tracking:
x_center = 300
y_center = 300
y_start_threshold = 50

center_line_x1, center_line_y1 = 300, 0
center_line_x2, center_line_y2 = 300, 600

turn_start = False

# TODO: 1. Print quadrant of ball in frame
start_time = 0
accumulator = 0
game_start_trigger = False
first_run = False

game_side_accumulator = 0
game_side_start_time = 0

score = {0: 0, 1: 0}

def check_game_start(center):
    # State tracking to start game through CV ball position persistence detection:
    global y_start_threshold, start_time, accumulator, game_start_trigger, first_run
                
    if center < y_start_threshold and start_time == 0:
        start_time = time.time()
        print(start_time)
                    
    # If condition is not true anymore:
    elif center > y_start_threshold:
        # Reset accumulator and start_time to defaults:
        accumulator = 0
        start_time = 0
                
    elif center < y_start_threshold and start_time != 0:
        accumulator = time.time() - start_time
        print("Accumulator: ", accumulator)
        if accumulator > 3:
            print("Game started")
            game_start_trigger = True
            first_run = True
            accumulator = 0
            start_time = 0
    
# Game loop when start trigger is True:
def game_start(center):
    # Player identification: 0, 1
    # Score tracking: Dictionary {Player_ID: Score}
        
    # Start a fresh game:
    global score
    global first_run
        
    print("Score", score)
    
    if first_run:
        start_side = get_ball_side(center)
        print("Start Side: ", start_side)
        score = score_tracking(center)
        first_run = False
    
    else:
        print("Game Running!")
        score_tracking(center)
        print(get_ball_side(center))
        # start_game_score(center)
    
def score_tracking(center):
    # Once game starts, start accumulator duration to track how long ball has stayed on the same side:
    global game_side_accumulator
    global game_side_start_time
    global first_run
    global score
    print(score)

    # Let time out be 3 seconds for each side.
    game_side_start_time = time.time()
    
    # We have to track both previous and current ball side state
    curr_side = get_ball_side(center)
    
    # A naive approach for score tracking is as follows:
    # 1. We only care about the side that loses the point.
    # 2. Losing:
    #     2.1 Ball time-out
    #     2.2 Ball went outside field of view
    
    # We will focus on 2.1 for now.
    
    # Ball time-out requires tracking the period for which ball remains within either half of the FOV.
    game_side_accumulator = 0
    game_side_start_time = time.time()
    
    game_side_accumulator = time.time() - accumulator
    print(game_side_accumulator)
    
    if game_side_accumulator > 3:
        if curr_side == 0:
            score[1] = score[1] + 1
        else:
            score[0] = score[0] + 1
    print(score[0])
    if score[0] >= 11 or score[1] >= 11:
        return score
    
def get_ball_side(center):
    if center[0] > y_center:
        return 1
    elif center[0] <= y_center:
        return 0

# Keep looping:
while True:
    # Grab the current frame:
    frame = vs.read()
    
    # Handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame
    
    # If we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video:
    if frame is None:
        break
    
    # Resize the frame, blur it, and convert it to the HSV color space:
    frame = imutils.resize(frame, width = 600, height = 600)
    
    frame_split_line_thickness = 2
    cv2.line(frame, (center_line_x1, center_line_y1), (center_line_x2, center_line_y2), (255, 0, 255), thickness = frame_split_line_thickness)
        
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
        
        
    
    # Construct a mask for the color "yello", then perform
    # a series of dilations and erosions to remove any small blobs left in the mask
    
    mask = cv2.inRange(hsv, yellowLower, yellowUpper)
    mask = cv2.erode(mask, None, iterations = 2)
    mask = cv2.dilate(mask, None, iterations = 2)
    
    # Find contours in the mask and initialize the current
    # (x, y) center of the ball
    
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    
    # Only proceed if at least one contour was found
    if len(cnts) == 0:
        accumulator = 0
        start_time = 0
        start_trigger = False
    
    if len(cnts) > 0:
        print(cnts)
        # Find the largest contour in th emask, then use
        # it to compute the minmum enclosing circle and
        # centroid
        c = max(cnts, key = cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
        if game_start_trigger:
            game_start(center)
        if center[0] > x_center:
                
            if center[1] < y_center:
                print("Quadrant 1")
                
                if center[1] < y_start_threshold:
                    print("Game Start Trigger Initiated!")
                    
                    check_game_start(center[1])
            
            elif center[1] > y_center:
                print("Quadrant 4")
                accumulator = 0
                start_time = 0
                                # State tracking to start game:
                # if center[1] < y_start_threshold:
                  
                  # print("Game Start Trigger Initiated!")
                    
                    # State tracking to start game through CV ball position persistence detection:
                    # check_game_start(center[1])
                

        elif center[0] < x_center:
            if center[1] > y_center:
                print("Quadrant 3")
                accumulator = 0
                start_time = 0
  
            elif center[1] < y_center:
                print("Quadrant 2")
                
                if center[1] < y_start_threshold:
                    print("Game Start Trigger Initiated!")
                    
                    check_game_start(center[1])
        
        # Only proceed if the radius meets a minimum size:
        if radius > 10:
            # Draw the circle and centroid on the frame
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            print("Radius: ", radius)
            
    # update the points queue
    pts.appendleft(center)
    
    # Loop over the set of tracked points:
    for i in range(1, len(pts)):
        # If either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue
        
        # Otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
    
    # Show the frame to our screen:
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    
    # If the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# If we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()
    
# Otherwise, release the cmaera
else:
    vs.release()
    
# Close all windows
cv2.destroyAllWindows()



