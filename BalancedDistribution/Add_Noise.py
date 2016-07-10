import pandas
from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils
import numpy as np
import pandas
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from keras.layers.recurrent import LSTM, SimpleRNN, GRU
def reConstruction(window_size,data,label):
    newdata = []
    newlabel = []
    L = len(data)
    D = len(data[0])
    interval = 1

    index = 0
    newdata_count = 0
    initial_value = -999
    while index+window_size < L:
        newdata.append(initial_value)
        newlabel.append(initial_value)
        Sequence = []
        for i in range(window_size):
            Sequence.append(data[index+i])
            newlabel[newdata_count] = label[index+i]
        index += interval
        newdata[newdata_count]=Sequence
        newdata_count += 1
    return np.array(newdata),np.array(newlabel)

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)
dataframe = pandas.read_csv("B_C_N_S_Multi.txt", header=None)
dataset = dataframe.values
print(dataset.shape)
X = dataset[:, 0:33].astype(float)
print(X)

columns = list(dataframe.columns.values)
columns.pop(-1)
print(columns)
from sklearn.preprocessing import StandardScaler,Normalizer

scale = Normalizer()

X[columns] = scale.fit_transform(X[columns])

print(X)

Y = dataset[:, 33]
print(Y.shape)


X,Y = reConstruction(20,X,Y)

# encode class values as integers
encoder = LabelEncoder()
encoder.fit(Y)
encoded_Y = encoder.transform(Y)
# convert integers to dummy variables (i.e. one hot encoded)
dummy_y = np_utils.to_categorical(encoded_Y)
print(dummy_y)

print(len(X[0]))
lstm_object = LSTM(50, input_length=len(X[0]), input_dim=33)


# define baseline model
def baseline_model():
    # create model
    model = Sequential()
    model.add(lstm_object)
    model.add(Dense(output_dim=4,activation='sigmoid'))
    #model.add(Dense(40, input_dim=33, init='normal', activation='relu'))
    #model.add(Dense(4, init='normal', activation='sigmoid'))
    # Compile model
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

estimator = KerasClassifier(build_fn=baseline_model, nb_epoch=10, batch_size=200, verbose=0)
kfold = KFold(n=len(X), n_folds=3, shuffle=False, random_state=seed)
results = cross_val_score(estimator, X, dummy_y, cv=kfold)
print("Baseline: %.2f%% (%.2f%%)" % (results.mean() * 100, results.std() * 100))
print(len(X[0]))
