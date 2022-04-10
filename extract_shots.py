import json
import numpy as np
import pandas as pd


# load data.json
with open(r"data.json", "r") as f:
    events = json.load(f)

# filter to only shot events
shots = [shot for shot in events if shot['type']['name'] == 'Shot']

print("Found {} shots". format(len(shots)))

print(shots[0])

shot = shots[0]['shot']

# calculate angle between two points

# Features to use
# x location
x_coord = shots[0]["location"][0],
y_coord = shots[0]["location"][1],
body_part = shot['body_part']['name'],

# angle_from_goal_center =

# shot type:
# 