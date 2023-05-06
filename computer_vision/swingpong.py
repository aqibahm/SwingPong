# Import the necessary packages:
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

# Establish video source through argument parsing:
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help = "path to the (optional) video file")
ap.add_argument("-b", "--buffer", type = int, default = 64, help = "max buffer size")
args = vars(ap.parse_args())

# If a video path was not supplied, grab the reference
# to the webcam:
    
# Allow the camera or video file to warm up
time.sleep(2.0)

class SwingPong:
    # Class attributes for game tracking:
    x_center = 300
    y_center = 300
    y_start_threshold = 50

    center_line_x1, center_line_y1 = 300, 0
    center_line_x2, center_line_y2 = 300, 600

    turn_start = False

    # TODO: 1. Print quadrant of ball in frame

    # Class attributes for ball tracking:
    yellowLower = (1, 78, 207)
    yellowUpper = (64, 255, 255)
    pts = deque(maxlen=args["buffer"])

    def __init__(self):
        self.start_time = 0
        self.accumulator = 0
        self.game_entry_tracker_flag = True
        self.game_start_tracker_flag = False
        self.score = {0: 0, 1: 0}

        if not args.get("video", False):
            self.vs = VideoStream(src = 0).start()

        # otherwise, grab a reference to the video file:
        else:
            self.vs = cv2.VideoCapture(args["video"])

        self.GameHandler()

    def ReturnScore(self):
        return self.score

    def GameHandler(self):
        # Conditions dependent on the various boolean flags:
        # Condition 1: Latent Ball Tracking Phase
        while True:
            # Condition 1: Game hasn't started, default to tracking ball position to start accumulator and trigger game start:
            if self.game_entry_tracker_flag and not self.game_start_tracker_flag:
                print("Entered Game Entry Tracker.")
                self.GameEntryTracker()

            # Condition 2: Game has started, track ball between the two regions and update score accordingly:
            if self.game_start_tracker_flag and not self.game_entry_tracker_flag:
                print("Entered Game State Tracker.")
                self.GameTracking()
                self.game_start_tracker_flag = False
                self.game_entry_tracker_flag = False

            # Condition 3: Game has finished, return score visualization and update game flags accordingly:
            if not self.game_entry_tracker_flag and not self.game_start_tracker_flag:
                print("Entered Game Score Visualization.")
                self.GameResults()
                self.game_entry_tracker_flag = True
                # Update game_state_tracker_flag and game_entry_tracker_flag inside self.GameResults() definition

    def GameTracking(self):
        while True and self.game_start_tracker_flag:
            # Grab the current frame:
            frame = self.vs.read()

            # Handle the frame from VideoCapture or VideoStream
            frame = frame[1] if args.get("video", False) else frame

            # If we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video:
            if frame is None:
                break

            # Resize the frame, blur it, and convert it to the HSV color space:
            frame = imutils.resize(frame, width = 600, height = 600)

            frame_split_line_thickness = 2
            cv2.line(frame, (self.center_line_x1, self.center_line_y1), (self.center_line_x2, self.center_line_y2), (255, 0, 255), thickness = frame_split_line_thickness)

            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            # Construct a mask for the color "yello", then perform
            # a series of dilations and erosions to remove any small blobs left in the mask

            mask = cv2.inRange(hsv, self.yellowLower, self.yellowUpper)
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

                # if self.game_start_trigger:
                #     pass
                if center[0] > self.x_center:

                    if center[1] < self.y_center:
                        print("Quadrant 1 in Game Tracking Phase.")

                        if center[1] < self.y_start_threshold:

                            # check_game_start(center[1])
                            self.StartTracking(center[1])

                    elif center[1] > self.y_center:
                        print("Quadrant 4 in Game Tracking Phase.")
                        # self.accumulator = 0
                        # self.start_time = 0
                        #                 State tracking to start game:
                        if center[1] < self.y_start_threshold:
                            self.StartTracking(center[1])


                elif center[0] < self.x_center:
                    if center[1] > self.y_center:
                        print("Quadrant 3 in Game Tracking Phase.")
                        accumulator = 0
                        start_time = 0

                    elif center[1] < self.y_center:
                        print("Quadrant 2 in Game Tracking Phase.")

                        if center[1] < self.y_start_threshold:
                            self.StartTracking(center[1])

                # Only proceed if the radius meets a minimum size:
                if radius > 10:
                    # Draw the circle and centroid on the frame
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                               (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    print("Radius: ", radius)

            # update the points queue
            self.pts.appendleft(center)

            # Loop over the set of tracked points:
            for i in range(1, len(self.pts)):
                # If either of the tracked points are None, ignore
                # them
                if self.pts[i - 1] is None or self.pts[i] is None:
                    continue

                # Otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)

                cv2.line(frame, self.pts[i - 1], self.pts[i], (0, 0, 255), thickness)

            # Show the frame to our screen:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # If the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break

        # # If we are not using a video file, stop the camera video stream
        # if not args.get("video", False):
        #     self.vs.stop()

        # # Otherwise, release the cmaera
        # else:
        #     self.vs.release()

        # # Close all windows
        # cv2.destroyAllWindows()
        
        print("Game Tracking Started!")

    def GameResults(self):
        print("Placeholder Game Results.")

    def GameEntryTracker(self):
        while True and self.game_entry_tracker_flag:
            # Grab the current frame:
            frame = self.vs.read()

            # Handle the frame from VideoCapture or VideoStream
            frame = frame[1] if args.get("video", False) else frame

            # If we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video:
            if frame is None:
                break

            # Resize the frame, blur it, and convert it to the HSV color space:
            frame = imutils.resize(frame, width = 600, height = 600)

            frame_split_line_thickness = 2
            cv2.line(frame, (self.center_line_x1, self.center_line_y1), (self.center_line_x2, self.center_line_y2), (255, 0, 255), thickness = frame_split_line_thickness)

            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)




            # Construct a mask for the color "yello", then perform
            # a series of dilations and erosions to remove any small blobs left in the mask

            mask = cv2.inRange(hsv, self.yellowLower, self.yellowUpper)
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

                # if self.game_start_trigger:
                #     pass
                if center[0] > self.x_center:

                    if center[1] < self.y_center:
                        print("Quadrant 1")

                        if center[1] < self.y_start_threshold:

                            # check_game_start(center[1])
                            self.StartTracking(center[1])

                    elif center[1] > self.y_center:
                        print("Quadrant 4")
                        # self.accumulator = 0
                        # self.start_time = 0
                        #                 State tracking to start game:
                        if center[1] < self.y_start_threshold:
                            self.StartTracking(center[1])


                elif center[0] < self.x_center:
                    if center[1] > self.y_center:
                        print("Quadrant 3")
                        accumulator = 0
                        start_time = 0

                    elif center[1] < self.y_center:
                        print("Quadrant 2")

                        if center[1] < self.y_start_threshold:
                            self.StartTracking(center[1])

                # Only proceed if the radius meets a minimum size:
                if radius > 10:
                    # Draw the circle and centroid on the frame
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                               (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    print("Radius: ", radius)

            # update the points queue
            self.pts.appendleft(center)

            # Loop over the set of tracked points:
            for i in range(1, len(self.pts)):
                # If either of the tracked points are None, ignore
                # them
                if self.pts[i - 1] is None or self.pts[i] is None:
                    continue

                # Otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)

                cv2.line(frame, self.pts[i - 1], self.pts[i], (0, 0, 255), thickness)

            # Show the frame to our screen:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # If the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break

        # # If we are not using a video file, stop the camera video stream
        # if not args.get("video", False):
        #     self.vs.stop()

        # # Otherwise, release the cmaera
        # else:
        #     self.vs.release()

        # # Close all windows
        # cv2.destroyAllWindows()

    
        

    def BallDetection(self):
        # Return centroid of segmented ball:
        # Keep looping:
    
        while True:
            # Grab the current frame:
            frame = self.vs.read()

            # Handle the frame from VideoCapture or VideoStream
            frame = frame[1] if args.get("video", False) else frame

            # If we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video:
            if frame is None:
                break

            # Resize the frame, blur it, and convert it to the HSV color space:
            frame = imutils.resize(frame, width = 600, height = 600)

            frame_split_line_thickness = 2
            cv2.line(frame, (self.center_line_x1, self.center_line_y1), (self.center_line_x2, self.center_line_y2), (255, 0, 255), thickness = frame_split_line_thickness)

            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)




            # Construct a mask for the color "yello", then perform
            # a series of dilations and erosions to remove any small blobs left in the mask

            mask = cv2.inRange(hsv, self.yellowLower, self.yellowUpper)
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

                if self.game_start_trigger:
                    pass
                if center[0] > self.x_center:

                    if center[1] < self.y_center:
                        print("Quadrant 1")

                        if center[1] < self.y_start_threshold:
                            self.StartTracking(center[1])

                    elif center[1] > self.y_center:
                        print("Quadrant 4")
                        # self.accumulator = 0
                        # self.start_time = 0
                        #                 State tracking to start game:
                        if center[1] < self.y_start_threshold:      
                            self.StartTracking(center[1])

                elif center[0] < self.x_center:
                    if center[1] > self.y_center:
                        print("Quadrant 3")
                        accumulator = 0
                        start_time = 0

                    elif center[1] < self.y_center:
                        print("Quadrant 2")

                        if center[1] < self.y_start_threshold:
                            self.StartTracking(center[1])

                # Only proceed if the radius meets a minimum size:
                if radius > 10:
                    # Draw the circle and centroid on the frame
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                               (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    print("Radius: ", radius)

            # update the points queue
            self.pts.appendleft(center)

            # Loop over the set of tracked points:
            for i in range(1, len(self.pts)):
                # If either of the tracked points are None, ignore
                # them
                if self.pts[i - 1] is None or self.pts[i] is None:
                    continue

                # Otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)

                cv2.line(frame, self.pts[i - 1], self.pts[i], (0, 0, 255), thickness)

            # Show the frame to our screen:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # If the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break

        # If we are not using a video file, stop the camera video stream
        if not args.get("video", False):
            self.vs.stop()

        # Otherwise, release the cmaera
        else:
            self.vs.release()

        # Close all windows
        cv2.destroyAllWindows()
    

    def StartTracking(self, center):
        if center < self.y_start_threshold and self.start_time == 0 and self.game_entry_tracker_flag:
            self.start_time = time.time()
            print(self.start_time)

        # If condition is not true anymore:
        elif center > self.y_start_threshold and not self.game_entry_tracker_flag:
            # Reset accumulator and start_time to defaults:
            self.accumulator = 0
            self.start_time = 0

        elif center < self.y_start_threshold and self.start_time != 0 and self.game_entry_tracker_flag:
            self.accumulator = time.time() - self.start_time
            print("Accumulator: ", self.accumulator)
            if self.accumulator > 3:
                self.accumulator = 0
                self.start_time = 0
                self.game_entry_tracker_flag = False
                self.game_start_tracker_flag = True
                # self.StartGame(center)
                print("Game Started!")
                

    def StartGame(self, center):
        # Notation for player-side tracking.
        # The half of the screen that has the ball will be considered the starting side:
        
        # TODO: Get starting side of the game.
        # TODO: Instantiate a dictionary to keep track of either side's score; represent starting side with 0, other side with 1
        if center < self.y_center:
            print("Side 0.")
        else: 
            print("Side 1.")



game = SwingPong()