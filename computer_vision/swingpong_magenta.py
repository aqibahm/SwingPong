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

    score_line_x1, score_line_y1 = 0, 300
    score_line_x2, score_line_y2 = 600, 300

    # TODO: 1. Print quadrant of ball in frame

    # Class attributes for ball tracking:
    yellowLower = (148, 70, 76)
    yellowUpper = (163, 153, 246)
    # yellowLower = (53, 65, 113)
    # yellowUpper = (90, 103, 188)
    
    pts = deque(maxlen=args["buffer"])

    def __init__(self):
        self.start_time = 0
        self.accumulator = 0
        self.first_serve = 0
        self.curr_serve = 0
        self.game_entry_tracker_flag = True
        self.game_start_tracker_flag = False
        self.first_serve_flag = True

        self.score_changed = False

        self.rallies = []
        self.first_run = True

        self.score = {0: 0, 1: 0}

        if not args.get("video", False):
            self.vs = VideoStream(src = 0).start()

        # otherwise, grab a reference to the video file:
        else:
            self.vs = cv2.VideoCapture(args["video"])

        self.GameHandler()

    def ReturnScore(self):
        return self.score

    def cv_draw_label(self, img, text, pos, bg_color):
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.7
        color = (0, 0, 0)
        thickness = cv2.FILLED
        margin = 2
        txt_size = cv2.getTextSize(text, font_face, scale, thickness)

        end_x = pos[0] + txt_size[0][0] + margin
        end_y = pos[1] - txt_size[0][1] - margin

        cv2.rectangle(img, pos, (end_x, end_y), bg_color, thickness)
        cv2.putText(img, text, pos, font_face, scale, color, 1, cv2.LINE_AA)

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

    def GameHistory(self):
        pass

    def ResetGame(self):
        pass

    def SetBallZone(self, center):
        if self.first_serve_flag:
            self.first_serve = False
            if center[0] < self.y_center:
                print("Side 0")
                self.serve_start_zone = 0
                self.curr_serve = 0

            elif center[0] > self.y_center:
                print("Side 1")
                self.first_serve = 1
                self.curr_serve = 1
                self.past_ball_zone = 1
                self.curr_ball_zone = 1

        else:
            self.past_ball_zone = self.curr_ball_zone
            if center[0] < self.y_center:
                self.curr_ball_zone = 0
            elif center[0] > self.y_center:
                self.curr_ball_zone = 0


    def GameTracking(self):
        # TODO: 
        # Mechanics of play:
        # 1. At the start of the game, the starting turn side is determined.
        # 1.1 During each turn, we need to keep track of the past turn side and the current turn side. 
        # 2. The starting side is the reference point for future score increments.
        # 3. The first turn is different, in that it instantiates the value of the starting side. 
        # 4. All subsequent shots are dependent on scoring changes and previous side values.
        # 5. Since the starting side persists across a game, it is ideal to store it as a static variable.
        # 6. We also need a first run flag, such that we can differentiate between the first turn of the game and the subsequent ones.
        # 7. Following the start of each turn, we skim the frame to find the ball.
        # 8. We know that the ball starts in the starting turn side.
        # 9. As soon as a ball is detected in a region, a timer starts.
        # 10. If the ball stays in the region for longer than expected, or does not make it to the other side within a window of time, the other side scores.
        # 11. If the other side scored, change current turn side to their side. Otherwise, if the current side scored, maintain the same flow as earlier.
        # 12. Mechanism to instantiate serve: Similar to the entry tracking mechanism.

        # Check whether this is the first serve:
        rally = []

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
            cv2.line(frame, (self.score_line_x1, self.score_line_y1), (self.score_line_x2, self.score_line_y2), (255, 0, 255), thickness = frame_split_line_thickness)

            score_string = str(self.score[0]) + " -- " + str(self.score[1])
            self.cv_draw_label(frame, 'Game Tracking On', (20,20), (255, 255, 255))
            self.cv_draw_label(frame, score_string, (500, 20), (255, 255, 255))

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
                pass

            # TODO: Make score increase only once.

            if len(rally) == 0:
                past_rally_length = 0
                curr_rally_length = 0
                self.accumulator = 0
                self.start_time = time.time()
            else:
                if max(self.score.values()) == 11:
                    self.game_start_tracker_flag = False
                    self.game_entry_tracker_flag = False
                past_rally_length = curr_rally_length
                curr_rally_length = len(rally)
                self.accumulator = time.time() - self.start_time
                

                # TODO: 
                # 1. Check if curr_rally_length == past_rally_length
                if self.accumulator > 3:
                    if curr_rally_length == past_rally_length:
                        self.accumulator = 0
                        self.rallies.append(rally)
                        if rally[-1] == 0:
                            self.score[1] += 1
                        elif rally[-1] == 1:
                            self.score[0] += 1
                            
                        time.sleep(5)

                        rally = []
                        print("Rallies: ", self.rallies)
                        print("Score: ", self.score)
                        

                    # if max(self.score.values()) == 11:
                    #     self.game_start_tracker_flag = False
                    #     self.game_entry_tracker_flag = False

            # Whichever zone it stays in for too long loses the point.


            # Accumulator should change value outside of the contour detection branch.
            # Check if rally list length has changed. 
            if len(cnts) > 0:
                print(rally)
                # print(cnts)
                # Find the largest contour in th emask, then use
                # it to compute the minmum enclosing circle and
                # centroid
                c = max(cnts, key = cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # Accumulator strategy:
                # As soon as an element is added to the rally list, reset accumulator.
                # If accumulator runs out of time, append current rally to self.rallies
                # Set rally = []
                # As soon as first rally element condition is satisfied, start accumulator. 
                # Reset accumulator if list growth times out.
                # Instead of checking for list growth, check for list appends.
                # 
                # If first serve: check if starting side is same self.serve_start_side:
                # Reset accumulator every time the ball reaches a new zone, which means the rally list gets a new element.

                if len(rally) == 0:
                    self.accumulator = 0
                    self.start_time = time.time()
                    self.score_changed = False
                    self.SetBallZone(center)
                
                # if self.accumulator > 3:
                #     self.score_changed = True
                #     self.rallies.append(rally)
                #     rally = []
                #     print("Starting new rally.")
                #     print(self.rallies)
                #     time.sleep(5)

                if center[1] > self.score_line_y1 and center[0] < self.y_center:
                    # Ball in one zone:
                    if len(rally) == 0 or rally[-1] != 0:
                        self.accumulator = 0
                        self.start_time = time.time()
                        rally.append(0)
                        
                

                elif center[1] > self.score_line_y1 and center[0] > self.y_center:
                    # Ball in one zone:
                    if len(rally) == 0 or rally[-1] != 1:
                        self.accumulator = 0
                        self.start_time = time.time()
                        rally.append(1)

            
                # TODO: Game Score Tracking:
                # if first_run:
                #     first_run = False
                #     self.SetBallZone(center)
                # # Start accumulator and track for scoring and rally list growth conditions.

                # # Scoring condition:
                # if center[0] < self.x_center and center[1] < self.y_score:


                # if center[0] > self.x_center:

                #     if center[1] < self.y_center:
                #         print("Quadrant 1 in Game Tracking Phase.")

                #         if center[1] < self.y_start_threshold:

                #             # check_game_start(center[1])
                #             self.StartTracking(center[1])

                #     elif center[1] > self.y_center:
                #         print("Quadrant 4 in Game Tracking Phase.")
                #         # self.accumulator = 0
                #         # self.start_time = 0
                #         #                 State tracking to start game:
                #         if center[1] < self.y_start_threshold:
                #             self.StartTracking(center[1])


                # elif center[0] < self.x_center:
                #     if center[1] > self.y_center:
                #         print("Quadrant 3 in Game Tracking Phase.")
                #         accumulator = 0
                #         start_time = 0

                #     elif center[1] < self.y_center:
                #         print("Quadrant 2 in Game Tracking Phase.")

                #         if center[1] < self.y_start_threshold:
                #             self.StartTracking(center[1])

                # Only proceed if the radius meets a minimum size:
                if radius > 1:
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

    def StartRally(self, center):
        # Ideal to call StartRally for each game rally.
        # Conditions for starting a new rally (Probably score state tracking in Game Handler.)
        # Either side's score changes, which triggers a new rally.
        # Each rally has the same structure: serve, exchange, and score.
        # How does one model these abstractions?

        # What is it that we are tracking?
        # 1. Changes to the game score.
        # 2. Differentiating between serve or exchanges based on ball center intersection with line.
        # 3. Whether scoring condition is satisfied: to increment score on either side.
        # 4. Changed game score should trigger a flag, which makes the Game Handler start a new rally.
        # 5. Rallies should proceed until 11 points are achieved on either side. 
        
        # How are rallies triggered in terms of program flow?
        # As soon as a new game is triggered, the CV part detects whether it is a new run or not.
        # We check for first_run to ensure that the starting side is established for relative scoring; this is persisted for the entirety of the game.
        # The CV loop should check for current score. If max[dict.values] < 11, continue to start a new rally.
        # Within a rally, we can track the state of the ball using a list.
        # Each list element will be a number, either 0 or 1.
        # Possible lists include [0, 1, 0, 1, ...] or [1, 0, 1, 0, ...]

        # The way we track time out is through the time it takes the list to grow. 
        # If, for example, the list takes more than 3 seconds to grow, we can assume that ball is not returned for the current game.
        # The last element of the list indicates the latest zone of the ball.
        # If the latest zone is 1, say, and the list stops growing, we can assume that player 1 did not return the ball successfully.
        # Same as above for zone 0
        # If the list stops growing at list element 1, we award a point to player 0
        # Similarly, if the list stops growing at list element 0, we award a point to player 1

        # Depending on the state of the list for the rally.
        # It might be ideal to have Game IDs for each game, as well as list tracking for the various rallies.
        # For now, we can assume that there is only one game for each run.
        # 

        # Criterion for legal rally increments, each list element is different from the last element.

        # Edge cases: Distinguishing between serve and general exchanges. 
        # The first list element must always be the zone for the serving zone.
        # For example, if first_serve_side is 0, rally should start with 0.
        # We update first_serve_side every time score changes, which is triggered by a check on the list element's growth.
        # Score change should trigger first_run flag as well.

        # Accumulator starts, condition for ball intersection at serve side.
        # x < x' and y < y', where x' denotes the scoring line and y' represents the line separating zones 0 and 1.

        # 
        pass
        
    def TrackScore(self, center):
        # TODO: 
        
        # 1.
        # Check if ball is at the same side as the self.first_serve variable for recognition density:
        # if center[0] < self.y_center:
        #     print("Side 0")
        #     self.first_serve = 0
        #     self.curr_serve = 0

        # elif center[0] > self.y_center:
        #     print("Side 1")
        #     self.first_serve = 1
        #     self.curr_serve = 1

        # Variables to consider: 
        # 1. center - coordinates of tracked ball in the frame.
        # 2. self.first_serve - integer [0, 1] denoting starting serve side.
        # 3. self.curr_serve - integer [0, 1] denoting current serve side.
        # 4. self.past_ball_zone - integer [0, 1]
        # 5. self.curr_ball_zone - integer [0, 1]

        # Note that ball zone updates for this iteration have taken place already within the calling function
        # Logic:
        # 1. What might be the condition to start the accumulator?
        # 1.1 The accumulator is tracking the persistence of the ball in one region.
        # 1.2 The accumulator should start at the TrackScore function's invokation.
        # 1.3 Start the accumulator
        # 2. Timer runs out, assume that ball stays in zone for 3 seconds, including any extremely high trajectories.

        # What about higher parabolic trajectories, where the ball may escape the frame for a little while and leave a time window where there is no ball detected?
        # We will get back to this.

        # For now, assume that this function has to change class variables to persist beyond CV computations.
        
        # What is the accumulator reset condition?
        # Either the ball changes its zone,
        # Or the timer runs out.


        # Instead of checking for time spent in each zone, we can instead check for the entry into and exit from
        # a rectangular plane parallel and adjacent to the table.

        # This would imply knowing the following:
        # 1. We can treat the rectangle as a horizontal line in the frame. A parallel line underneath this line can serve as the reference point with the table.
        # 2. From the scoring line's perspective:
        #   2.1. If it is the serve, the ball must intersect with the line twice, once in zone 0 and once in zone 1.
        #   2.2. If it is not the serve, the ball must intersect with the line once, precisely in the zone opposite to the returning player's zone.
        #   2.3.  

        if self.curr_ball_zone == self.past_ball_zone:
            self.accumulator = time.time() - self.start_time
            print("Current accumulator: ", self.accumulator)
        
            if self.accumulator > 3:
                # Time out condition, increment opponent's score:
                print("Opponent scored!")
                print(self.score)
                for i in range(5):
                    time.sleep(1)
                    print("Starting next rally in: ", i, " seconds.")
    
    def GameResults(self):
        print("Game Score Results: ", self.score)
        print("Rally history: ", self.rallies)

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
            cv2.line(frame, (self.score_line_x1, self.score_line_y1), (self.score_line_x2, self.score_line_y2), (255, 0, 255), thickness = frame_split_line_thickness)

            self.cv_draw_label(frame, 'Bring Ball Here To Start New Game.', (100, 20), (255, 255, 255))

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

# class Game:
#     def __init__(self):
#         self.id = 

# class Rally:
#     def __init__(self):



game = SwingPong()
