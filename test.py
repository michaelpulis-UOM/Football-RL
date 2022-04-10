import json
from create_dataset import  CreateDataset


# open the events data
with open(r"events\3788741.json") as f:
    events = json.load(f)

# open the tracking data
with open(r"three-sixty\3788741.json") as f:
    tracking = json.load(f)

events_array = []

# loop through the events data and extract the id
for item in events:
    events_array.append(item['id'])

tracking_array = []

# loop through the events data and extract the event_uuid
for item in tracking:
    tracking_array.append(item['event_uuid'])

joined = []

for item in tracking_array:
    if item in events_array:
        joined.append(item)

print(len(events_array))
print(len(tracking_array))
print(len(joined))

dataset_maker = CreateDataset()

# dataset_maker.loadFile(file_location=r"events\3788741.json")
# dataset_maker.loadTrackingContent(file_location=r"events\3788741.json")

dataset_maker.loadTrackingContentFromDir('three-sixty/*.json')
# dataset_maker.loadFilesFromDir('events/*.json', filterGamesWithoutTrackingData=True)

print(len(dataset_maker.tracking_content))
# print(len(dataset_maker.events))

# x, y, rewards, events, t = dataset_maker.createImageDataset()
# print(len(y))