import cv2
from create_dataset import CreateDataset


ds = CreateDataset()
ds.loadTrackingContentFromDir('three-sixty/*.json')
ds.file_limit = 1
ds.loadFilesFromDir('events/*.json', filterGamesWithoutTrackingData=True)
observations, actions, rewards, event_ids, terminals = ds.createImageDataset()

print(observations.shape)
# resize observations[0] to twice its size
large = cv2.resize(observations[0][0], (0, 0), fx=2, fy=2)
large2 = cv2.resize(observations[0][1], (0, 0), fx=2, fy=2)
large3 = cv2.resize(observations[0][2], (0, 0), fx=2, fy=2)

cv2.imshow('large', large)
cv2.imshow('large2', large2)
cv2.imshow('large3', large3)
                                                 
cv2.waitKey(0)