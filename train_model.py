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
    hidden1 = Dense(6, activation='relu', kernel_initializer='he_normal')(visible)
    hidden2 = Dense(5, activation='relu', kernel_initializer='he_normal')(hidden1)
    hidden3 = Dense(5, activation='relu', kernel_initializer='he_normal')(hidden2)
    # classification output
    out_clas = Dense(output_dims, activation='softmax')(hidden3)
    # regression output
    out_reg = Dense(2, activation='linear')(hidden3)
    # define model
    model = Model(inputs=visible, outputs=[out_clas, out_reg])
    # compile the keras model
    model.compile(loss=['categorical_crossentropy', 'mse'], optimizer='adam')
    return model

def getDataset():
    datasetMaker = CreateDataset()
    datasetMaker.loadFilesFromDir('events/*.json')

    return datasetMaker.createDataset()

def main():
    # x, y = getDataset()
    # model = create_model(x.shape[1], y.shape[1])
    # model.fit(x,y, batch_size=32, epochs=150)

    datasetMaker = CreateDataset()
    datasetMaker.loadFilesFromDir('events/*.json')
    # datasetMaker.loadFile('data.json')
    x, y_class, y_pos = datasetMaker.createDatasetMultY()


    print(len(x))
    model = create_model_multiple_prediction(x.shape[1], y_class.shape[1])
    model.fit(x, [y_class, y_pos], batch_size=32, epochs=20)

    model.save('models/model1')

def main2():
    model = tf.keras.models.load_model('models/model1')
    model.summary()

    datasetMaker = CreateDataset()
    datasetMaker.loadFile('data.json')
    # datasetMaker.loadFilesFromDir('events/*.json')

    x, y_class, y_pos = datasetMaker.createDatasetMultY()

    print("Length: ", len(x))
    to_predict = np.array(x[:][:10])
    predictions = model.predict(to_predict)
    to_predict_actions, to_predict_pos = predictions[0], predictions[1]

    visualiser = Visualiser()
    visualiser.showPredictions(to_predict, predictions)

if __name__ == "__main__":
    # main()
    main2()