#This project is based on the ChunML tuutorial https://github.com/ChunML/text-generator/blob/master
import numpy as np

#-------------------------FUNCTIONS TO HELP LOAD DATA-----------------------------------------------#

#Lets first define some functions to import our data from txt files
def generate_text(model, length, vocab_size, ix_to_char):
    #Start with a random character first as int
    ix = [np.random.randint(vocab_size)]
    #match that int to the character in our dictionary
    y_char = [ix_to_char[ix[-1]]]
    X = np.zeros((1,length,vocab_size))
    for i in range(length):
        #append the last predicted character to the sequence
        X[0,i,:][ix[-1]] = 1
        print(ix_to_char[ix[-1]], end="")
        ix = np.argmax(model.predict(X[:,:i+1,:])[0],1)
        y_char.append(ix_to_char[ix[-1]])
    return ('').join(y_char)

#Method for preparing the training data
def load_data(data_dir, seq_length):
    data = open(data_dir,'r').read()
    chars = list(set(data))
    VOCAB_SIZE = len(chars)

    print('Data length: {} characters'.format(len(data)))
    print('Vocabulary size: {} characters'.format(VOCAB_SIZE))

    ix_to_char = {ix:char for ix, char in enumerate(chars)}
    char_to_ix = {char:ix for ix, char in enumerate(chars)}

    X = np.zeros((len(data)//seq_length, seq_length, VOCAB_SIZE))
    y = np.zeros((len(data)//seq_length, seq_length, VOCAB_SIZE))
    for i in range(0, len(data)//seq_length):
        X_sequence = data[i*seq_length:(i+1)*seq_length]
        X_sequence_ix = [char_to_ix[value] for value in X_sequence]
        input_sequence = np.zeros((seq_length, VOCAB_SIZE))
        for j in range(seq_length):
            input_sequence[j][X_sequence_ix[j]] = 1
            X[i] = input_sequence

        y_sequence = data[i*seq_length+1:(i+1)*seq_length+1]
        y_sequence_ix = [char_to_ix[value] for value in y_sequence]
        target_sequence = np.zeros((seq_length, VOCAB_SIZE))
        for j in range(seq_length):
            target_sequence[j][y_sequence_ix[j]] = 1
            y[i] = target_sequence
    return X,y,VOCAB_SIZE,ix_to_char

#--------------------------------MODEL------------------------------------------------------#

import matplotlib.pyplot as plt
import time
import csv
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM, SimpleRNN
from keras.layers.wrappers import TimeDistributed
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('-data_dir', default='./data/jessie_input.txt')
ap.add_argument('-batch_size', type=int, default=50)
ap.add_argument('-layer_num', type=int, default=2)
ap.add_argument('-seq_length', type=int, default=50)
ap.add_argument('-hidden_dim', type=int, default=500)
ap.add_argument('-generate_length', type=int, default=500)
ap.add_argument('-np_epoch', type=int, default=20)
ap.add_argument('-mode', default='train')
ap.add_argument('-weights', default='')
args = vars(ap.parse_args())

DATA_DIR = args['data_dir']
BATCH_SIZE = args['batch_size']
HIDDEN_DIM = args['hidden_dim']
SEQ_LENGTH = args['seq_length']
WEIGHTS = args['weights']

GENERATE_LENGTH = args['generate_length']
LAYER_NUM = args['layer_num']

#Lets create the training data
X, y, VOCAB_SIZE, ix_to_char = load_data(DATA_DIR,SEQ_LENGTH)

#Create and compile the network
model = Sequential()
model.add(LSTM(HIDDEN_DIM, input_shape=(None, VOCAB_SIZE), return_sequences=True))
for i in range(LAYER_NUM-1):
    model.add(LSTM(HIDDEN_DIM, return_sequences=True))
model.add(TimeDistributed(Dense(VOCAB_SIZE)))
model.add(Activation('softmax'))
model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

#Generate some sample before training to know how bad it is
generate_text(model, args['generate_length'], VOCAB_SIZE, ix_to_char)

if not WEIGHTS == '':
    model.load_weights(WEIGHTS)
    nb_epoch = int(WEIGHTS[WEIGHTS.rfind('_')+1:WEIGHTS.find('_')])
else:
    nb_epoch = 0

#Training if there are not trained weights specified
if args['mode'] == 'train' or WEIGHTS == '':
    while True:
        print('\n\nEpoch: {}\n'.format(nb_epoch))
        model.fit(X,y,batch_size=BATCH_SIZE, verbose=1, nb_epoch=1)
        nb_epoch +=1
        generate_text(model, GENERATE_LENGTH, VOCAB_SIZE, ix_to_char)
        if nb_epoch %10 == 0:
            model.save_weights('checkpoint_layer_{}_hidden_{}_epoch_{}_jessie.hdf5'.format(LAYER_NUM,HIDDEN_DIM,nb_epoch))

#Else load the train weights and perform generation only
elif WEIGHTS == '':
    #Loading trained weights
    model.load_weights(WEIGHTS)
    generate_text(model, GENERATE_LENGTH, VOCAB_SIZE, ix_to_char)
    print('\n\n')
else:
    print('\n\nNothing to do!')


