import cv2
import numpy as np
import json
import itertools
from itertools import tee, zip_longest
import matplotlib.pyplot as plt
from math import sqrt
from create_dataset import CreateDataset

class Visualiser():
    def __init__(self):
        self.content = []
        self.passes = []

        dataset = CreateDataset()

        self.rows = dataset.xT_Map.shape[0]
        self.cols = dataset.xT_Map.shape[1]
        self.height, self.width = 80, 120
        self.stats_h, self.stats_w = 10,120

        self.ratio = 6
        self.blank_image = np.zeros((self.height*self.ratio, self.width*self.ratio,3), np.uint8)
        self.stats_image = np.zeros((self.stats_h*self.ratio, self.stats_w*self.ratio,3), np.uint8)

        self.font                   = cv2.FONT_HERSHEY_SIMPLEX
        self.fontScale              = 0.5
        self.fontColor              = (255,255,255)
        self.lineType               = 2  

        self.global_wait = 4
        self.per_frame = 3

        self.colours = [(0,0,255), (255,0,0)]
        self.teams = {}

        self.counter = 0
        self.firstTeam = None

    def loadTrackingContent(self, path):
        with open(path, 'r') as file:
            raw_tracking = json.loads(file.read())

        self.tracking_content = {}
        for item in raw_tracking:
            self.tracking_content[item['event_uuid']] = item

    def loadContent(self, path):
        with open(path, 'r') as j:
            self.content = json.loads(j.read())

    def drawBall(self, image, position):
        circleThickness = 8
        cv2.circle(image, position, circleThickness, (0,242,255), thickness=-1, lineType=8, shift=0)

    def drawPlayerLight(self, image, event):
        circleThickness = 15
        p_p = (int(event['location'][0] * self.ratio), int(event['location'][1] * self.ratio))
        cv2.circle(image, p_p, circleThickness, (0,242,255), thickness=-1, lineType=cv2.LINE_AA, shift=0)


        for player in event['shot']['freeze_frame']:
            position = (int(player['location'][0] * self.ratio), int(player['location'][1] * self.ratio))
            c = (0,0,255) if player['teammate'] else (255,0,0)
            cv2.circle(image, position, circleThickness, c, thickness=-1, lineType=cv2.LINE_AA, shift=0)

    def drawPlayer(self, image, under_pressure, player, colour, position):
        circleThickness = 10
        cv2.circle(image, position, circleThickness, colour, thickness=-1, lineType=8, shift=0)
        # if(under_pressure):
        #     cv2.circle(image, position, circleThickness*2, (0,242,255), thickness=1, lineType=8, shift=0)

        if(player != None):
            jerseyNumberWidth = cv2.getTextSize( str(self.player_details[player]['number']), self.font, 0.5, 1)[0][0]
            posLabelWidth = cv2.getTextSize( str(self.player_details[player]['position']), self.font, 0.5, 1)[0][0]

            textPos = (int(position[0]) - int(jerseyNumberWidth/2), int(position[1]+circleThickness/2))
            posPos = (int(position[0]) - int(posLabelWidth/2), int(position[1]+circleThickness/2) + int(circleThickness *1.5))

            cv2.putText(image, str(self.player_details[player]['number']), textPos, self.font, 0.5, self.fontColor, 1, cv2.LINE_AA)
            cv2.putText(image, str(self.player_details[player]['position']), posPos, self.font, 0.5, self.fontColor, 1, cv2.LINE_AA)
        
    def getColour(self, team_id):
        if(not (team_id in self.teams)):
            self.teams[team_id] = self.colours[len(self.teams) - 1]

        return self.teams[team_id]

    def draw_lines(self, image, ratio):
        image = cv2.rectangle(image, (0 * ratio, 0 * ratio), (120 * ratio, 80 * ratio), (255, 255, 255), 3)
        
        image = cv2.rectangle(image, (0 * ratio, 18 * ratio), (18 * ratio, 62 * ratio), (255, 255, 255), 3)
        image = cv2.rectangle(image, (0 * ratio, 30 * ratio), (6 * ratio, 50 * ratio), (255, 255, 255), 3)
        
        image = cv2.rectangle(image, (102 * ratio, 18 * ratio), (120 * ratio, 62 * ratio), (255, 255, 255), 3)
        image = cv2.rectangle(image, (114 * ratio, 30 * ratio), (120 * ratio, 50 * ratio), (255, 255, 255), 3)

        image = cv2.rectangle(image, (0 * ratio, 36 * ratio), (1 * ratio, 44 * ratio), (255, 255, 255), 3)
        image = cv2.rectangle(image, (119 * ratio, 36 * ratio), (120 * ratio, 44 * ratio), (255, 255, 255), 3)
        # image = cv2.rectangle(image, (114 * ratio, 30 * ratio), (120 * ratio, 50 * ratio), (255, 255, 255), 3)
        
        image = cv2.rectangle(image, (0 * ratio, 0 * ratio), (60 * ratio, 80 * ratio), (255, 255, 255), 3)

        cv2.circle(image, (60 * ratio, 40 * ratio), 10 * ratio, (255,255,255), thickness=3, lineType=cv2.LINE_AA, shift=0)
        cv2.circle(image, (60 * ratio, 40 * ratio), 1 * ratio, (255,255,255), thickness=-1, lineType=cv2.LINE_AA, shift=0)

        return image

    def shorten_position(self, position):
        if(position == "Goalkeeper"): return "GK"
        else:
            return "".join([a[0] for a in position.split()])

    def fill_details(self, event):
        details = {}
        for item in event:
            details[item['player']['id']] = {}
            details[item['player']['id']]['name'] = item['player']['name']
            details[item['player']['id']]['position'] = self.shorten_position(item['position']['name'])
            details[item['player']['id']]['number'] = item['jersey_number']

        return details
    
    def encodeName (self, name):
        asciidata=name.encode("ascii","ignore")
        return asciidata.decode("utf-8") 

    def pairwise_tee(self, iterable):
        a, b = tee(iterable)
        next(b, None)
        return zip_longest(a, b)

    def showTime(self):
        
        blank_image = np.zeros((self.height * self.ratio, self.width * self.ratio,3), np.uint8)
        self.draw_lines(blank_image, self.ratio)
        self.frame_rate = 1
        self.global_wait = int(1000/self.frame_rate)
        counter = 0
        for frame in self.content:

            blank_image[:] = (18, 97, 41)
            blank_image = self.draw_lines(self.blank_image, self.ratio)

            visible_area = frame['visible_area']
            x_values = visible_area[::2]
            y_values = visible_area[1::2]

            needs_flip = False
            if(y_values[1] < y_values[len(y_values)-2]): needs_flip = True
            
            team_a = (255,0,0) 
            team_b = (0,0,255)

            if(needs_flip):
                team_a = (0,0,255)
                team_b = (255,0,0)


            for i in range(len(x_values))[:len(x_values)-2]:
                camera_x, camera_y = x_values[i], y_values[i]
                nCamera_x, nCamera_y = x_values[i+1], y_values[i+1]

                if(needs_flip):
                    camera_x = 120-camera_x
                    camera_y = 80-camera_y
                    nCamera_x = 120-nCamera_x
                    nCamera_y = 80-nCamera_y

                cv2.line(blank_image, (int(camera_x) * self.ratio, int(camera_y) * self.ratio), (int(nCamera_x) * self.ratio, int(nCamera_y) * self.ratio), (0,0,0))
            
            for player in frame['freeze_frame']:

                x, y = player['location'][0], player['location'][1]
                
                if(needs_flip):
                    x = 120 - x
                    y = 80 - y

                

                location = (int(x) * self.ratio, int(y) * self.ratio) 
                colour = team_a if player['teammate'] else team_b

                # if(player['actor']): colour = (0,255,0)
                self.drawPlayer(blank_image, player['actor'], None, colour, location)

            cv2.putText(blank_image, f"Frame: {counter}", (10,15), self.font, self.fontScale, self.fontColor, self.lineType)
            cv2.putText(blank_image, f"PC   : {len(frame['freeze_frame'])}", (10,35), self.font, self.fontScale, self.fontColor, self.lineType)
            cv2.putText(blank_image, f"NF   : {needs_flip}", (10,55), self.font, self.fontScale, self.fontColor, self.lineType)
            cv2.imshow("tracking", blank_image)
            c = cv2.waitKey(self.global_wait)

            counter += 1

            if c == 27:
                exit()

    def drawAllPlayers(self, blank_image, colours, id):
        frame = self.tracking_content[id]
        visible_area = frame['visible_area']
        x_values = visible_area[::2]
        y_values = visible_area[1::2]

        needs_flip = True
        if(y_values[1] >= y_values[len(y_values)-2]): needs_flip = False
        
        team_a = (255,0,0) 
        team_b = (0,0,255)

        if(needs_flip):
            team_a = (0,0,255)
            team_b = (255,0,0)


        for i in range(len(x_values))[:len(x_values)-2]:
            camera_x, camera_y = x_values[i], y_values[i]
            nCamera_x, nCamera_y = x_values[i+1], y_values[i+1]

            if(needs_flip):
                camera_x = 120-camera_x
                camera_y = 80-camera_y
                nCamera_x = 120-nCamera_x
                nCamera_y = 80-nCamera_y

            cv2.line(blank_image, (int(camera_x) * self.ratio, int(camera_y) * self.ratio), (int(nCamera_x) * self.ratio, int(nCamera_y) * self.ratio), (0,0,0))
        
        for player in frame['freeze_frame']:

            x, y = player['location'][0], player['location'][1]
            
            if(needs_flip):
                x = 120 - x
                y = 80 - y

            

            location = (int(x) * self.ratio, int(y) * self.ratio) 
            colour = team_a if player['teammate'] else team_b

            # if(player['actor']): colour = (0,255,0)
            self.drawPlayer(blank_image, player['actor'], None, colour, location)

    def drawPassLines(self, image, position):
        passLineWidth = 5
        x, y = position 

        cv2.line(image, (x-self.ratio*passLineWidth, 0), (x-self.ratio*passLineWidth, 120*self.ratio), (0,255,0))
        cv2.line(image, (x+self.ratio*passLineWidth, 0), (x+self.ratio*passLineWidth, 120*self.ratio), (0,255,0))

    def show(self):
        self.homeTeamName = self.content[0]['team']['name']
        self.awayTeamName = self.content[1]['team']['name']

        self.home_details = {}
        self.away_details = {}

        self.player_details = self.fill_details(self.content[0]['tactics']['lineup'] + self.content[1]['tactics']['lineup'])
        counter = 0
        for event, nextEvent in self.pairwise_tee(self.content):

            if(event['type']['name'] == "Pressure"): continue

            if(self.firstTeam == None):
                self.firstTeam = event['team']['id']

            counter+=1
            self.blank_image = np.zeros((self.height * self.ratio, self.width * self.ratio,3), np.uint8)
            self.stats_image = np.zeros((self.stats_h * self.ratio, self.stats_w * self.ratio,3), np.uint8)

            self.blank_image[:] = (18, 97, 41)
            self.stats_image[:] = (0, 0, 0)

            key = None
            if(event['type']['name'] == "Carry"): key = "carry"
            elif(event['type']['name'] == "Pass"): key = "pass"
            elif(event['type']['name'] == "Ball Receipt*"): key = "ball_receipt"
            elif(event['type']['name'] == "Shot"): key = "shot"
            elif(event['type']['name'] == "Pressure"): key = "pressure"
            elif(event['type']['name'] == "Clearance"): key = "clearance"
            else: 
                continue
                self.blank_image[:] = (18, 97, 41)
                print(event['type']['name'])
                cv2.putText(self.stats_image, f"({counter}): {event['type']['name']}", (10,15), self.font, self.fontScale, self.fontColor, self.lineType)

                cv2.imshow(f" {self.homeTeamName} vs {self.awayTeamName}", self.blank_image)
                c = cv2.waitKey(2000)
                if c == 27:
                    exit()

                cv2.imshow(f" {self.homeTeamName} vs {self.awayTeamName}", self.stats_image)
                cv2.waitKey(self.global_wait)
                continue
            
                
            # if(key != "shot"):continue
            # continue
            start_location = []
            start_location.append(event['location'][0])
            start_location.append(event['location'][1])

            self.getColour(event['team']['id'])
            if(event['team']['id'] != self.firstTeam):
                start_location[0] = 120-start_location[0]
                start_location[1] = 80-start_location[1]

            end_location = []
            
            if(key in event and 'end_location' in event[key]):
                end_location.append(event[key]['end_location'][0])
                end_location.append(event[key]['end_location'][1])

                if(event['team']['id'] != self.firstTeam):
                    end_location[0] = 120-end_location[0]
                    end_location[1] = 80-end_location[1]

            startX = int(start_location[0] * self.ratio)
            startY = int(start_location[1] * self.ratio)

            xStep, yStep = None, None

            step_count = 500
            if(key in event and 'end_location' in event[key]):
                xStep = ((int(end_location[0]) * self.ratio) - startX)/step_count
                yStep = ((int(end_location[1]) * self.ratio) - startY)/step_count

            if(key == 'ball_receipt'):  step_count=5

            current_related_event = None
            # if('related_events' in event and len(event['related_events']) > 0 and event['related_events'][0] in self.tracking_content):
            #     current_related_event = event['related_events'][0]
                

            for i in range(step_count):
                self.blank_image[:] = (18, 97, 41)
                self.stats_image[:] = (0, 0, 0)

                if(current_related_event != None):
                    pass
                    
                    # self.drawAllPlayers(self.blank_image, self.getColour(event['team']['id']), current_related_event)

                self.blank_image = self.draw_lines(self.blank_image, self.ratio)
                cv2.putText(self.stats_image, f"({counter}): {key} -- {self.homeTeamName if event['team']['id'] == self.firstTeam else self.awayTeamName }", (10,15), self.font, self.fontScale, self.fontColor, 1, cv2.LINE_AA)
                
                if(key in event and 'end_location' in event[key]):
                    cv2.putText(self.stats_image, f"({int((startX+(xStep*i))/self.ratio)}, {int((startY+(yStep*i))/self.ratio)})", (10,35), self.font, self.fontScale, self.fontColor, 1, cv2.LINE_AA)
                else:
                    cv2.putText(self.stats_image, f"({int(startX/self.ratio)}, {int(startY/self.ratio)})", (10,35), self.font, self.fontScale, self.fontColor, 1, cv2.LINE_AA)

                if(key == "shot"):
                    self.drawPlayerLight(self.blank_image, event)
                    self.drawBall(self.blank_image, (int(startX+(xStep*i)), int(startY+(yStep*i))))
                    cv2.putText(self.stats_image, f"xG: {event['shot']['statsbomb_xg']}", (200,15), self.font, self.fontScale, self.fontColor, self.lineType)

                    
                    
                elif(key == "carry"):
                    cv2.putText(self.stats_image, f"{self.encodeName(event['player']['name'])}", (150,35), self.font, self.fontScale, self.fontColor, 1, cv2.LINE_AA)
                    cv2.putText(self.stats_image, f"Pressure: {'under_pressure' in event}", (400,15), self.font, self.fontScale, self.fontColor, 1, cv2.LINE_AA)
                    self.drawPlayer(self.blank_image, 'under_pressure' in event, event['player']['id'], self.getColour(event['team']['id']), (int(startX+(xStep*i)), int(startY+(yStep*i))))

                    # draw an arrowed line to the midpoint
                    start_point =  (int(start_location[0] * self.ratio), int(start_location[1]) * self.ratio)
                    end_point = (int(end_location[0] * self.ratio), int(end_location[1] * self.ratio))
                    length = sqrt( (mid_point[0] - start_point[0])**2 + (mid_point[1] - start_point[1])**2 )

                    cv2.arrowedLine(self.blank_image, start_point, end_point, (0,0,0), 4, cv2.LINE_AA, 0, 20/length)
                    # cv2.line(self.blank_image, mid_point, end_point, (0,0,0), 4, cv2.LINE_AA)
                elif(key == "ball_receipt"):
                    cv2.putText(self.stats_image, f"Pressure: {'under_pressure' in event}", (400,15), self.font, self.fontScale, self.fontColor, 1, cv2.LINE_AA)
                    cv2.putText(self.stats_image, f"{self.encodeName(event['player']['name'])}", (150,35), self.font, self.fontScale, self.fontColor, 1, cv2.LINE_AA)
                    self.drawPlayer(self.blank_image,'under_pressure' in event, event['player']['id'], self.getColour(event['team']['id']), (int(startX), int(startY)))
                
                elif(key == "pass"):
                    # print(event['id'])
                    cv2.putText(self.stats_image, f"Pressure: {'under_pressure' in event}", (400,15), self.font, self.fontScale, self.fontColor, 1, cv2.LINE_AA)
                    if('recipient' in event['pass']):
                        cv2.putText(self.stats_image, f"{self.encodeName(event['player']['name'])} to {self.encodeName(event['pass']['recipient']['name'])}", (100,35), self.font, self.fontScale, self.fontColor, 1, cv2.LINE_AA)
                        
                    # draw an arrowed line to the midpoint
                    start_point =  (int(start_location[0] * self.ratio), int(start_location[1]) * self.ratio)
                    end_point = (int(end_location[0] * self.ratio), int(end_location[1]* self.ratio))
                    mid_point = (int((start_point[0] + end_point[0])/2), int((start_point[1] + end_point[1])/2))

                    length = sqrt( (mid_point[0] - start_point[0])**2 + (mid_point[1] - start_point[1])**2 )

                    cv2.arrowedLine(self.blank_image, start_point, mid_point, (0,0,0), 4, cv2.LINE_AA, 0, 20/length)
                    cv2.line(self.blank_image, mid_point, end_point, (0,0,0), 4, cv2.LINE_AA)

                    # self.drawBall(self.blank_image, (int(startX+(xStep*i)), int(startY+(yStep*i))))
                    self.drawPlayer(self.blank_image, 'under_pressure' in event, event['player']['id'], self.getColour(event['team']['id']), (int(start_location[0] * self.ratio), int(start_location[1]) * self.ratio))
                    if('recipient' in event['pass']):
                        self.drawPlayer(self.blank_image, False, event['pass']['recipient']['id'], self.getColour(event['team']['id']), (int(end_location[0]) * self.ratio, int(end_location[1]) * self.ratio))

                    # self.drawPassLines(self.blank_image, (startX, startY))

                if(nextEvent['type']['name'] == 'Pressure'):
                    next_start_location = []
                    next_start_location.append(nextEvent['location'][0])
                    next_start_location.append(nextEvent['location'][1])

                    if(nextEvent['team']['id'] != self.firstTeam):
                        next_start_location[0] = 120-next_start_location[0]
                        next_start_location[1] = 80-next_start_location[1]
                    self.drawPlayer(self.blank_image, False, nextEvent['player']['id'], self.getColour(nextEvent['team']['id']), (int(next_start_location[0] * self.ratio), int(next_start_location[1] * self.ratio)))

                cv2.imshow(f" {self.homeTeamName} vs {self.awayTeamName}", self.blank_image)
                cv2.imshow(f" {self.homeTeamName} vs {self.awayTeamName} -- Statistics Viewer", self.stats_image)
                c = cv2.waitKey(self.per_frame)
                if c == 27:
                    exit()

            else:
                continue

            cv2.imshow(f" {self.homeTeamName} vs {self.awayTeamName}", self.blank_image)
            cv2.waitKey(self.global_wait)

    def loadPredictions(self, x, predictions):
        self.x = x
        self.predictions = predictions
        # self.show()

    def showPredictions(self, x, predictions, model):
        datasetMaker = CreateDataset()
        predicted_actions, predicted_x, predicted_y = predictions[0], predictions[1], predictions[2]
        time_wait = 0
        i = 0
        interactive = False
        self.interactive_action = 0
        self.interactive_x = 120/2
        self.interactive_y = 80/2
        predicted_interactive_action = None
        while(True):

            if(interactive):
                predicted_interactive_action = model.predict(np.array([[self.interactive_action, self.interactive_x, self.interactive_y]]))

            self.blank_image = np.zeros((self.height * self.ratio, self.width * self.ratio,3), np.uint8)
            self.blank_image[:] = (18, 97, 41)
            self.blank_image = self.draw_lines(self.blank_image, self.ratio)

            current_action = None
            if(not interactive):
                current_action = datasetMaker.ID_to_str[np.argmax(predicted_actions[i])]
            else:
                current_action = self.interactive_action

            # Old position
            if(not interactive):
                self.drawPlayer(self.blank_image, False, None, (0,0,255), (int(x[i][1] * self.ratio), int(x[i][2]) * self.ratio))
            else:
                self.drawPlayer(self.blank_image, False, None, (0,0,255), (int(self.interactive_x * self.ratio), int(self.interactive_y) * self.ratio))

            # drawing the prediction

            if(not interactive):
                self.drawPlayer(self.blank_image, False, None, (255,0,0), (int(predicted_x[i] * 120 * self.ratio), int(predicted_y[i] * 80 * self.ratio)))
            else:
                inter_pred_x = predicted_interactive_action[1][0]
                inter_pred_y = predicted_interactive_action[2][0]

                self.drawPlayer(self.blank_image, False, None, (255,0,0), (int(inter_pred_x * 120 * self.ratio), int(inter_pred_y * 80 * self.ratio)))

            
            text_to_show = ""
            if(not interactive): text_to_show = f"Step {i} -- {'Paused' if time_wait == 0 else 'Playing'}" + " Predicted action: " + str(current_action)
            else: text_to_show = "Interactive Mode. Action: " + str(self.interactive_action)+ ":"+datasetMaker.ID_to_str[self.interactive_action]+ " X: " + str(self.interactive_x) + ", Y: " + str(self.interactive_y)
            
            cv2.putText(self.blank_image, text_to_show, (10,25), self.font, 0.5, self.fontColor, 1, cv2.LINE_AA)

            if(not interactive):
                cv2.arrowedLine(self.blank_image, (int(x[i][1] * self.ratio), int(x[i][2]) * self.ratio), (int(predicted_x[i] * 120 * self.ratio), int(predicted_y[i] * 80 * self.ratio)), (0,255,0), 4)
            else:
                cv2.arrowedLine(self.blank_image, (int(self.interactive_x * self.ratio), int(self.interactive_y * self.ratio)), (int(predicted_interactive_action[1] * 120 * self.ratio), int(predicted_interactive_action[2] * 80 * self.ratio)), (0,255,0), 4)
            
            window_title = f"Step {i} -- {'Paused' if time_wait == 0 else 'Playing'}"
            cv2.imshow("visualiser_window", self.blank_image)

            cv2.setMouseCallback('visualiser_window',  self.clicked)
            cv2.setWindowTitle("visualiser_window", window_title)

            if(not interactive):
                plt.bar([datasetMaker.ID_to_str[i] for i in range(len(datasetMaker.ID_to_str))], predicted_actions[i])
            else:
                plt.bar([datasetMaker.ID_to_str[i] for i in range(len(datasetMaker.ID_to_str))], np.array(predicted_interactive_action[0][0]))
            
            plt.savefig('tmp_chart.png')
            cv2.imshow("Probability Distribution for Actions", cv2.imread("tmp_chart.png"))

            if(not interactive): key_pressed = cv2.waitKey(time_wait)
            else: key_pressed = cv2.waitKey(int(1000/12) )
            # key_pressed = cv2.waitKey(time_wait)
            if(key_pressed == ord('j')):
                i -= 1
            elif(key_pressed == ord('l')):
                i += 1
            elif(key_pressed == ord(' ')):
                if(time_wait == 0): time_wait = 5000
                else: time_wait = 0
            elif(key_pressed == ord('q')):
                exit()
            elif(key_pressed == ord('i')):
                interactive = not(interactive)
            elif(key_pressed == -1):
                i += 1
            else:
                for i in range(len(datasetMaker.ID_to_str)):
                    if(key_pressed == ord(str(i))):
                        self.interactive_action = i
            if(i < 0): i = 0
            if(i >= len(x)):
                break

            plt.clf()
        
    def clicked(self, event, x, y, flag, param):

        if flag == cv2.EVENT_FLAG_LBUTTON or (event == cv2.EVENT_MOUSEMOVE and flag == cv2.EVENT_FLAG_LBUTTON):
            self.interactive_x = x/self.ratio
            self.interactive_y = y/self.ratio
            # cv2. destroyAllWindows() 

    def draw_zone(self, image, row, col, color):

        start_y = int(80*(row/self.rows))
        end_y = int(80*((row+1)/self.rows))

        start_x = int(120*(col/self.cols))
        end_x = int(120*((col+1)/self.cols))

        image = cv2.rectangle(image, (start_x * self.ratio, start_y * self.ratio), (self.ratio * end_x, self.ratio * end_y), color, -1)

        return (self.ratio* int((start_x+end_x)/2), self.ratio*int((start_y+end_y)/2))

    def arrow_between(self, image, start_point, end_point):
        
        mid_point = (int((start_point[0] + end_point[0])/2), int((start_point[1] + end_point[1])/2))
        length = sqrt( (mid_point[0] - start_point[0])**2 + (mid_point[1] - start_point[1])**2 )

        cv2.arrowedLine(image, start_point, end_point, (0,0,0), 4, cv2.LINE_AA, 0, 20/length)

    def visualise_sequence(self, sequence, chunks, prediction, actual):
        pred =  CreateDataset().ID_to_str[prediction]

        split_ar = np.array_split(sequence, len(sequence)/chunks)
        zipped_sequence = zip(split_ar, split_ar[1:])

        
        counter = 0
        

        for current_state, next_state in zipped_sequence:

            self.blank_image[:] = (18, 97, 41)
            self.stats_image[:] = (0, 0, 0)

            self.blank_image = self.draw_lines(self.blank_image, self.ratio)

            current_row, current_col = int(current_state[1]), int(current_state[2])
            next_row, next_col = int(next_state[1]), int(next_state[2])

            start_point = self.draw_zone(self.blank_image, current_row, current_col, (0,0,255))
            end_point = self.draw_zone(self.blank_image, next_row, next_col, (255,0,0))

            if(not(current_row == next_row and current_col == next_col)):
                self.arrow_between(self.blank_image, start_point, end_point)
                
            if(counter == chunks):
                cv2.putText(self.blank_image, "Prediction for BLUE: " + pred, (10,30), self.font, 0.5, self.fontColor, 1, cv2.LINE_AA)
            else:
                cv2.putText(self.blank_image, "CONTEXT", (10,30), self.font, 0.5, self.fontColor, 1, cv2.LINE_AA)
                
            cv2.putText(self.blank_image, "Actual:" + CreateDataset().ID_to_str[actual], (10,60), self.font, 0.5, self.fontColor, 1, cv2.LINE_AA)

            counter += 1

            cv2.imshow("sequence_show - "+pred, self.blank_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


visualiser = Visualiser()
# visualiser.loadContent('data.json')
# visualiser.loadTrackingContent('data_track.json')
# visualiser.loadContent('data_track.json')
# visualiser.showTime()
# visualiser.show()
# s = [ 0, 0 ,12, 2, 3, 14,  0,  2, 14,  0,  6, 14,  2,  5, 15]
# visualiser.showPredictions()

# visualiser.visualise_sequence(s, 3, 1)
