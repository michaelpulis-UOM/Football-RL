import cv2
from create_dataset import CreateDataset


ds = CreateDataset()
ds.loadTrackingContentFromDir('three-sixty/*.json')
# datasetMaker.file_limit = 5
ds.loadFilesFromDir('events/*.json', filterGamesWithoutTrackingData=True)
observations, actions, rewards, event_ids, terminals = ds.createImageDataset()

# showing

print(observations.shape)
print('avg', observations[0].mean()) 

cv2.imshow('image', observations[0][0])
cv2.imshow('image1', observations[0][1])
cv2.imshow('image12', observations[0][2])
                                                 
cv2.waitKey(0)