import cv2
import numpy as np
import json
import itertools


content = []
passes = []

with open("data.json", 'r') as j:
    content = json.loads(j.read())


height,width = 80, 120
stats_h, stats_w = 10,120

ratio = 5
blank_image = np.zeros((height*ratio,width*ratio,3), np.uint8)
stats_image = np.zeros((stats_h*ratio,stats_w*ratio,3), np.uint8)
time = 120

font                   = cv2.FONT_HERSHEY_SIMPLEX
fontScale              = 0.5
fontColor              = (255,255,255)
lineType               = 2  

global_wait = 2
per_frame = 1

def drawBall(image, position):
    circleThickness = 5
    cv2.circle(image, position, circleThickness, (0,242,255), thickness=-1, lineType=8, shift=0)

def drawPlayer(image, under_pressure, player, colour, position):
    circleThickness = 15
    cv2.circle(image, position, circleThickness, colour, thickness=-1, lineType=8, shift=0)
    if(under_pressure):
        cv2.circle(image, position, circleThickness*2, (0,242,255), thickness=1, lineType=8, shift=0)

    textPos = (int(position[0]-circleThickness/2), int(position[1]+circleThickness/2))
    posPos = (int(position[0]-circleThickness/1.5) , int(position[1]+circleThickness/2) + int(circleThickness *1.5))

    cv2.putText(image, str(player_details[player]['number']), textPos, font, 0.5, fontColor, 1, cv2.LINE_AA)
    cv2.putText(image, str(player_details[player]['position']), posPos, font, 0.5, fontColor, 1, cv2.LINE_AA)
    
def getColour(team_id):
    if(not (team_id in teams)):
        teams[team_id] = colours[len(teams) - 1]

    return teams[team_id]

def draw_lines(image, ratio):
    image = cv2.rectangle(image, (0 * ratio, 0 * ratio), (120 * ratio, 80 * ratio), (255, 255, 255), 3)
    
    image = cv2.rectangle(image, (0 * ratio, 18 * ratio), (18 * ratio, 62 * ratio), (255, 255, 255), 3)
    image = cv2.rectangle(image, (0 * ratio, 30 * ratio), (6 * ratio, 50 * ratio), (255, 255, 255), 3)
    
    image = cv2.rectangle(image, (102 * ratio, 18 * ratio), (120 * ratio, 62 * ratio), (255, 255, 255), 3)
    image = cv2.rectangle(image, (114 * ratio, 30 * ratio), (120 * ratio, 50 * ratio), (255, 255, 255), 3)
    
    image = cv2.rectangle(image, (0 * ratio, 0 * ratio), (60 * ratio, 80 * ratio), (255, 255, 255), 3)

    cv2.circle(image, (60 * ratio, 40 * ratio), 10 * ratio, (255,255,255), thickness=3, lineType=8, shift=0)
    cv2.circle(image, (60 * ratio, 40 * ratio), 1 * ratio, (255,255,255), thickness=-1, lineType=8, shift=0)

    return image

def encodeName (name):
    asciidata=name.encode("ascii","ignore")
    return asciidata.decode("utf-8") 

colours = [(0,0,255), (255,0,0)]
teams = {}

counter = 0
firstTeam = None

homeTeamName = content[0]['team']['name']
awayTeamName = content[1]['team']['name']

home_details = {}
away_details = {}

def shorten_position(position):
    if(position == "Goalkeeper"): return "GK"
    else:
        return "".join([a[0] for a in position.split()])

def fill_details(event):
    details = {}
    for item in event:
        details[item['player']['id']] = {}
        details[item['player']['id']]['name'] = item['player']['name']
        details[item['player']['id']]['position'] = shorten_position(item['position']['name'])
        details[item['player']['id']]['number'] = item['jersey_number']

    return details

player_details = fill_details(content[0]['tactics']['lineup'] + content[1]['tactics']['lineup'])

from itertools import tee, zip_longest

def pairwise_tee(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip_longest(a, b)

for event, nextEvent in pairwise_tee(content[25:250]):

    if(event['type']['name'] == "Pressure"): continue

    if(firstTeam == None):
        firstTeam = event['team']['id']

    counter+=1
    blank_image = np.zeros((height*ratio,width*ratio,3), np.uint8)
    stats_image = np.zeros((stats_h*ratio,stats_w*ratio,3), np.uint8)

    blank_image[:] = (18, 97, 41)
    stats_image[:] = (0, 0, 0)

    key = None
    if(event['type']['name'] == "Carry"): key = "carry"
    elif(event['type']['name'] == "Pass"): key = "pass"
    elif(event['type']['name'] == "Ball Receipt*"): key = "ball_receipt"
    elif(event['type']['name'] == "Shot"): key = "shot"
    elif(event['type']['name'] == "Pressure"): key = "pressure"
    elif(event['type']['name'] == "Clearance"): key = "clearance"
    else: 
        continue
        blank_image[:] = (18, 97, 41)
        print(event['type']['name'])
        cv2.putText(stats_image, f"({counter}): {event['type']['name']}", (10,15), font, fontScale, fontColor, lineType)

        cv2.imshow(f" {homeTeamName} vs {awayTeamName}", blank_image)
        c = cv2.waitKey(2000)
        if c == 27:
            exit()

        cv2.imshow(f" {homeTeamName} vs {awayTeamName}", stats_image)
        cv2.waitKey(global_wait)
        continue
    
    # continue
    start_location = []
    start_location.append(event['location'][0])
    start_location.append(event['location'][1])

    getColour(event['team']['id'])
    if(event['team']['id'] != firstTeam):
        start_location[0] = 120-start_location[0]
        start_location[1] = 80-start_location[1]

    end_location = []
    
    if(key in event and 'end_location' in event[key]):
        end_location.append(event[key]['end_location'][0])
        end_location.append(event[key]['end_location'][1])

        if(event['team']['id'] != firstTeam):
            end_location[0] = 120-end_location[0]
            end_location[1] = 80-end_location[1]

    startX = int(start_location[0] * ratio)
    startY = int(start_location[1] * ratio)

    xStep, yStep = None, None

    if(key in event and 'end_location' in event[key]):
        xStep = ((int(end_location[0]) * ratio) - startX)/100
        yStep = ((int(end_location[1]) * ratio) - startY)/100

    step_count = 100
    if(key == 'ball_receipt'):  step_count=5
    for i in range(step_count):
        blank_image[:] = (18, 97, 41)
        stats_image[:] = (0, 0, 0)
        blank_image = draw_lines(blank_image, ratio)
        cv2.putText(stats_image, f"({counter}): {key} -- {homeTeamName if event['team']['id'] == firstTeam else awayTeamName }", (10,15), font, fontScale, fontColor, 1, cv2.LINE_AA)
        
        if(key in event and 'end_location' in event[key]):
            cv2.putText(stats_image, f"({int((startX+(xStep*i))/ratio)}, {int((startY+(yStep*i))/ratio)})", (10,35), font, fontScale, fontColor, 1, cv2.LINE_AA)
        else:
            cv2.putText(stats_image, f"({int(startX/ratio)}, {int(startY/ratio)})", (10,35), font, fontScale, fontColor, 1, cv2.LINE_AA)

        if(key == "carry"):
            cv2.putText(stats_image, f"{encodeName(event['player']['name'])}", (150,35), font, fontScale, fontColor, 1, cv2.LINE_AA)
            cv2.putText(stats_image, f"Pressure: {'under_pressure' in event}", (400,15), font, fontScale, fontColor, 1, cv2.LINE_AA)
            drawPlayer(blank_image, 'under_pressure' in event, event['player']['id'], getColour(event['team']['id']), (int(startX+(xStep*i)), int(startY+(yStep*i))))
        elif(key == "ball_receipt"):
            cv2.putText(stats_image, f"Pressure: {'under_pressure' in event}", (400,15), font, fontScale, fontColor, 1, cv2.LINE_AA)
            cv2.putText(stats_image, f"{encodeName(event['player']['name'])}", (150,35), font, fontScale, fontColor, 1, cv2.LINE_AA)
            drawPlayer(blank_image,'under_pressure' in event, event['player']['id'], getColour(event['team']['id']), (int(startX), int(startY)))
        
        elif(key == "pass"):
            cv2.putText(stats_image, f"Pressure: {'under_pressure' in event}", (400,15), font, fontScale, fontColor, 1, cv2.LINE_AA)
            cv2.putText(stats_image, f"{encodeName(event['player']['name'])} to {encodeName(event['pass']['recipient']['name'])}", (100,35), font, fontScale, fontColor, 1, cv2.LINE_AA)
            drawBall(blank_image, (int(startX+(xStep*i)), int(startY+(yStep*i))))
            drawPlayer(blank_image, 'under_pressure' in event, event['player']['id'], getColour(event['team']['id']), (int(start_location[0] * ratio), int(start_location[1]) * ratio))
            drawPlayer(blank_image, False, event['pass']['recipient']['id'], getColour(event['team']['id']), (int(end_location[0]) * ratio, 
                                    int(end_location[1]) * ratio))


        if(nextEvent['type']['name'] == 'Pressure'):
            next_start_location = []
            next_start_location.append(nextEvent['location'][0])
            next_start_location.append(nextEvent['location'][1])

            if(nextEvent['team']['id'] != firstTeam):
                next_start_location[0] = 120-next_start_location[0]
                next_start_location[1] = 80-next_start_location[1]
            drawPlayer(blank_image, False, nextEvent['player']['id'], getColour(nextEvent['team']['id']), (int(next_start_location[0] * ratio), int(next_start_location[1] * ratio)))

        cv2.imshow(f" {homeTeamName} vs {awayTeamName}", blank_image)
        cv2.imshow(f" {homeTeamName} vs {awayTeamName} -- Statistics Viewer", stats_image)
        c = cv2.waitKey(per_frame)
        if c == 27:
            exit()

    else:
        continue

    cv2.imshow(f" {homeTeamName} vs {awayTeamName}", blank_image)
    cv2.waitKey(global_wait)