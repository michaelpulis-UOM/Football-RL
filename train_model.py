from keras.models import Sequential
from keras.layers import Dense	
from keras.models import Model
from keras.layers import Input
import tensorflow as tf
import numpy as np

from create_dataset import CreateDataset
from view import Visualiser

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

def create_model_multiple_prediction(input_dims, output_dims):   
    # create model
    visible = Input(shape=(input_dims,))
    hidden1 = Dense(6, activation='relu')(visible)
    hidden2 = Dense(5, activation='relu')(hidden1)
    hidden3 = Dense(5, activation='relu')(hidden2)
    # classification output
    out_clas = Dense(output_dims, activation='softmax')(hidden3)
    # regression output
    out_pos_x = Dense(1, activation='relu')(hidden3)
    out_pos_y = Dense(1, activation='relu')(hidden3)
    # define model
    model = Model(inputs=visible, outputs=[out_clas, out_pos_x, out_pos_y])
    # compile the keras model
    model.compile(loss=['categorical_crossentropy', 'mse', 'mse'], optimizer='adam')
    return model

def getDataset():
    datasetMaker = CreateDataset()
    datasetMaker.loadFilesFromDir('events/*.json')

    return datasetMaker.createDataset()

def train():
    
    datasetMaker = CreateDataset()
    datasetMaker.loadFilesFromDir('events/*.json')
    datasetMaker.saveFiles("test")

    x, y_class, y_pos_x, y_pos_y = datasetMaker.createDatasetMultY()

    h = [0 for i in range(len(datasetMaker.ID_to_str))]
    for i in y_class: h[np.argmax(i)] += 1
    
    print(h)
    np.save("all", {'x':x, 'y_class':y_class, 'y_pos_x':y_pos_x, 'y_pos_y':y_pos_y})

    model = create_model_multiple_prediction(x.shape[1], y_class.shape[1])
    model.fit(x, [y_class, y_pos_x, y_pos_y], batch_size=32, epochs=80)

    model.save('models/model1')

def predict():
    model = tf.keras.models.load_model('models/model1')
    model.summary()

    datasetMaker = CreateDataset()

    # datasetMaker.loadFile("tmp_store")
    datasetMaker.loadFile('data.json')
    # datasetMaker.loadFilesFromDir('events/*.json')
    datasetMaker.saveFiles("tmp_store")
    
    x, _, _, _ = datasetMaker.createDatasetMultY()

    to_predict = np.array(x[:100])
    predictions = model.predict(to_predict)
    to_predict_actions, to_predict_pos = predictions[0], predictions[1]

    visualiser = Visualiser()
    visualiser.showPredictions(to_predict, predictions, model)

if __name__ == "__main__":
    # predict()
    # exit()

    n = input("0 - Train, 1 - Predict: ")
    if n == "0":
        train()
    elif n == "1":
        predict() 