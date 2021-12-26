from keras.models import Sequential
from keras.layers import Dense	
from create_dataset import CreateDataset


def create_model(input_dims, output_dims):   
    # create model
	model = Sequential()
	model.add(Dense(6, input_dim=input_dims, activation='relu'))
	model.add(Dense(5, activation='relu'))
	model.add(Dense(5, activation='relu'))
	model.add(Dense(output_dims, activation='softmax'))
	# Compile model
	model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model

def getDataset():
    datasetMaker = CreateDataset()
    datasetMaker.loadFilesFromDir('events/*.json')

    return datasetMaker.createDataset()

def main():
    x, y = getDataset()
    model = create_model(x.shape[1], y.shape[1])
    model.fit(x,y, batch_size=32, epochs=150)

if __name__ == "__main__":
    main()