'''Trains a LSTM on the IMDB sentiment classification task.

The dataset is actually too small for LSTM to be of any advantage
compared to simpler, much faster methods such as TF-IDF+LogReg.

Notes:

- RNNs are tricky. Choice of batch size is important,
choice of loss and optimizer is critical, etc.
Some configurations won't converge.

- LSTM loss decrease patterns during training can be quite different
from what you see with CNNs/MLPs/etc.
'''

from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility
import sys
import os
import random as RANDOM
from sklearn import svm,datasets,preprocessing,linear_model
from sklearn.metrics import roc_auc_score
from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers import Input, Dense
from keras.models import Model
from keras.layers.recurrent import LSTM, SimpleRNN, GRU
from keras.datasets import imdb
def LoadData(input_data_path,filename):
    """
    global input_data_path,out_put_pathmodified_negative
    #y_svmformat, x_svm_format = svm_read_problem(os.path.join(os.getcwd(),"AS_Path_Error_half_minutes.txt"))
    #y_svmformat, x_svm_format = svm_read_problem(os.path.join(os.getcwd(),"AS_Leak_half_minutes.txt"))
    #y_svmformat, x_svm_format = svm_read_problem(os.path.join(os.getcwd(),"AS_Filtering_Error_half_minutes.txt"))
    y_svmformat, x_svm_format = svm_read_problem(os.path.join(input_data_path,filename))
    #y_svmformat, x_svm_format = svm_read_problem(os.path.join(os.getcwd(),"Nimda_AS_513_half_minutes.txt"))
    #y_svmformat, x_svm_format = svm_read_problem(os.path.join(os.getcwd(),"Code_Red_I_AS_513_half_minutes.txt"))
    #y_svmformat, x_svm_format = svm_read_problem(os.path.join(os.getcwd(),"AS_Filtering_Error_AS_286_half_minutes.txt"))

    y_svmformat=np.array(y_svmformat)
    y_svmformat[y_svmformat==-1]=positive_sign#Positive is -1

    Data=[]
    for tab in range(len(x_svm_format)):
        Data.append([])
        temp=[]
        for k,v in x_svm_format[tab].items():
            temp.append(int(v))
        Data[tab].extend(temp)
        Data[tab].append(int(y_svmformat[tab]))
    Data=np.array(Data)
    np.random.shuffle(Data)
    np.random.shuffle(Data)
    return Data
    """
    global positive_sign,negative_sign,count_positive,count_negative,out_put_path,modified_negative,modified_positivei
    with open(os.path.join(input_data_path,filename)) as fin:
        if filename == 'sonar.dat':
            negative_flag = 'M'
        elif filename == 'bands.dat':
            negative_flag = 'noband'
        elif filename =='Ionosphere.dat':
            negative_flag = 'g'
        elif filename =='spectfheart.dat':
            negative_flag = 'g'
        elif filename =='spambase.dat':
            negative_flag = '0'
        elif filename =='page-blocks0.dat':
            negative_flag = 'negative'
        elif filename =='blocks0.dat':
            negative_flag = 'g'
        elif filename =='heart.dat':
            negative_flag = '2'
        elif filename =='segment0.dat':
            negative_flag = 'g'
        elif filename == 'BGP_DATA.txt':
            negative_flag = '1.0'
        elif filename == 'Code_Red_I.txt':
            negative_flag = '1.0'
        elif filename == 'Nimda.txt':
            negative_flag = '1.0'
        elif filename == 'Slammer.txt':
            negative_flag = '1.0'
        else:
            negative_flag = '1.0'
    #with open("AS_Filtering_Error_AS_286_half_minutes.txt") as fin:
        Data=[]

        for each in fin:
            if '@' in each:
                continue
            val=each.split(",")
            if len(val)>0 or val[-1].strip()=="negative" or val[-1].strip()=="positive":
                #print(each)
                if val[-1].strip()== negative_flag:
                    val[-1]=modified_negative
                    count_negative += 1
                else:
                    val[-1]= modified_positive
                    count_positive += 1
                try:
                    val=map(lambda a:float(a),val)
                except:
                    val=map(lambda a:str(a),val)

                val[-1]=int(val[-1])
                Data.append(val)
        Data=np.array(Data)
        return Data


def reConstruction(window_size,data,label):
    newdata = []
    newlabel = []
    L = len(data)
    D = len(data[0])
    #W = 20
    interval = 1
    index = 0
    newdata_count = 0
    initial_value = -999
    while index+window_size <= L:
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

def returnAllIndex(Data):
    temp = []
    for i in range(len(Data)):
        temp.append(i)
    return temp

def returnPositiveIndex(Data,positive_sign):
    temp = []
    for i in range(len(Data)):
        if Data[i][-1] == positive_sign:
            temp.append(i)
    return temp

def returnNegativeIndex(Data,negative_sign):
    temp = []
    for i in range(len(Data)):
        if Data[i][-1] == negative_sign:
            temp.append(i)
    return temp

def Convergge(X_Training,Y_Training,time_scale_size):
    window_size = len(X_Training[0])
    TEMP_XData = []
    N = window_size/time_scale_size
    for tab1 in range(len(X_Training)):
        TEMP_XData.append([])
        for tab2 in range(N):
            TEMP_Value = np.zeros((1,len(X_Training[0][0])))
            for tab3 in range(time_scale_size):
                TEMP_Value += X_Training[tab1][tab2*time_scale_size+tab3]
            TEMP_Value = TEMP_Value/time_scale_size
            TEMP_XData[tab1].append(list(TEMP_Value[0]))
    return  np.array(TEMP_XData),Y_Training

def Main(base_url,eachfile,bagging_number,window_size,lstm_size,bagging_label,time_scale_size):

    global positive_sign,negative_sign,count_positive,count_negative,input_data_path_training,input_data_path_testing,out_put_path,modified_positive,modified_negative

    if eachfile == "B_Code_Red_I.txt":
        Training_Data = LoadData(input_data_path_training,"B_N_S_Training.txt")
    elif eachfile == "B_Nimda.txt":
        Training_Data = LoadData(input_data_path_training,"B_C_S_Training.txt")
    elif eachfile == "B_Slammer.txt":
        Training_Data = LoadData(input_data_path_training,"B_C_N_Training.txt")
    Testing_Data=LoadData(input_data_path,eachfile)

    Positive_Data=Training_Data[Training_Data[:,-1]==modified_positive]
    Negative_Data=Training_Data[Training_Data[:,-1]==negative_sign]

    print("IR is :"+str(float(len(Negative_Data))/len(Positive_Data)))

    outputpath = os.path.join(base_url,"MultiEvent_Keras_B_"+str(bagging_label)+"_W_"+str(window_size))
    if not os.path.isdir(outputpath):
        os.makedirs(outputpath)
    outfutfilename1 = os.path.join(outputpath,"True_Label_"+"for_"+eachfile)

    print("bagging_number is "+str(bagging_number)+"----------")
    for t in range(1):
        np.random.seed(1337)  # for reproducibility
        X_Training=Training_Data[:,:-1]
        Y_Training=Training_Data[:,-1]

        X_Testing=Testing_Data[:,:-1]
        Y_Testing=Testing_Data[:,-1]

        scaler = preprocessing.StandardScaler()
        batch_size = 200
        (X_Training,Y_Training) = reConstruction(window_size,scaler.fit_transform(X_Training),Y_Training)
        (X_Testing,Y_Testing) = reConstruction(window_size,scaler.fit_transform(X_Testing),Y_Testing)

        with open(outfutfilename1,"w")as fout:
            np.savetxt(fout,Y_Testing)

        lstm_object = LSTM(lstm_size,input_length=window_size,input_dim=33)
        print('Build model...'+'Window Size is '+str(window_size)+' LSTM Size is '+str(lstm_size))
        model = Sequential()
        model.add(lstm_object)#X.shape is (samples, timesteps, dimension)
        model.add(Dense(output_dim=1))
        model.add(Activation("sigmoid"))
        model.compile( optimizer='adam',loss='binary_crossentropy',metrics=['accuracy'])

        X_Training,Y_Training = Convergge(X_Training,Y_Training,time_scale_size)
        X_Testing,Y_Testing = Convergge(X_Testing,Y_Testing,time_scale_size)

        model.fit(X_Training, Y_Training, batch_size=batch_size,nb_epoch=10)

        TempList=model.predict(X_Testing,batch_size=batch_size)

        outfutfilename2 = os.path.join(outputpath,"Bagging_Predict_"+"for_"+eachfile)

        with open(outfutfilename2,"a")as fout:
            fout.write("----------bagging_: "+str(bagging_number)+"th"+" window size: "+str(window_size)+" lstm_size: "+str(lstm_size)+"----------\n")
            np.savetxt(fout,TempList)


if __name__=="__main__":
    global positive_sign,negative_sign,count_positive,count_negative,input_data_path_training,input_data_path_testing,out_put_path,modified_positive,modified_negative
    positive_sign=-1
    negative_sign=1
    modified_positive = 0
    modified_negative = 1
    count_positive=0
    count_negative=0

    with open("Setting.txt")as fin:
        vallist = fin.readlines()
        baseurl, base_url = vallist[0].split(":")
        #windowsize,  window_size = vallist[2].split(":")
        #bagging, bagging_label= vallist[3].split(":")

    #base_url = base_url.strip()
    base_url = "/Users/chengmin/Dropbox/BLSTM"
    #base_url = "/home/grads/mcheng223/IGBB_Imbalanced"
    input_data_path = os.path.join(base_url,"MultiEvent")
    input_data_path_training =os.path.join(input_data_path,"Training")
    input_data_path_testing =input_data_path

    filenamelist=filter(lambda a:os.path.isfile(os.path.join(input_data_path,a)),os.listdir(input_data_path_testing))

    #total_args = list(sys.argv)
    #total_args.pop(0)

    #processing_file = 'B_'+str(total_args[0])+".txt"
    processing_file = "B_Slammer.txt"

    print("Start________________________on TESTING___**************:"+processing_file)

    #window_size = int(total_args[1])
    window_size = 30
    #bagging_label = int(total_args[2])
    bagging_label = 1
    #lstm_size = int(total_args[3])
    lstm_size_list = [10,15,20,25,30,35,40,45,50,55,60,70,80,90,100]
    #bagging_number = int(total_args[4])
    bagging_number = 1
    time_scale_size = 1
    #bagging_number = 1
    #bagging_label = 50
    #window_size = 30
    for lstm_size in lstm_size_list:
        Main(base_url,processing_file,bagging_number,window_size,lstm_size,bagging_label,time_scale_size)


"""
[98.937]
[100.0]
[99.471]
[99.479]
[99.478]
[99.4762713738578]


"""