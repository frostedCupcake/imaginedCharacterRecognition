# -*- coding: utf-8 -*-
"""BM5020_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IFG9ZJ_bhAFsmVSuM-QBmo9FDkQBaQcD
"""

import numpy as np
import pandas as pd


df = pd.read_csv('MW.csv')

df.describe()

df.head()

EEG_MAX = [i for i in range(1024)]

col_names = ["Digit", "Data points", *EEG_MAX]

df_cliped = pd.read_csv('MW.csv', names=col_names)

df_cliped.head()

raffa = df_cliped.iloc[0, :]

raffa[880:900]

df_cliped.drop(df_cliped.iloc[:, 890:], inplace=True, axis=1)

df_cliped.drop(['Data points'], axis=1, inplace=True)

df_cliped.head()

def normalize_row(row):
    return (row - row.min()) / (row.max() - row.min())

eeg_data = df_cliped.sample(frac=1).reset_index(drop=True)

eeg_data

eeg_data.iloc[:, 1:] = eeg_data.iloc[:, 1:].apply(normalize_row, axis=1)

eeg_data.head()

eeg_lables = pd.get_dummies(eeg_data['Digit'])

eeg_lables

eeg_lables.to_numpy()

import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(12, 6))
sns.lineplot(data=eeg_data.iloc[2, 1:], linewidth=3)

from sklearn.model_selection import train_test_split

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(eeg_data.iloc[:, 1:].to_numpy(), eeg_lables.to_numpy(), test_size=0.2, random_state=42)

# Split the train set into train and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.regularizers import l2
from tensorflow.keras.metrics import Precision, Recall
from keras import regularizers
from tensorflow.keras.layers import Conv2D, MaxPool2D, Flatten, Dense, Reshape, Conv1D, GlobalAveragePooling1D, MaxPooling1D,  BatchNormalization, Activation, Add, Input, ZeroPadding2D, AveragePooling2D,  Dropout, MaxPooling2D, Concatenate, GlobalAveragePooling2D, concatenate

from tensorflow.keras.layers import Input, Conv1D, BatchNormalization, DepthwiseConv1D, Activation, MaxPooling1D, Dropout, SeparableConv1D, concatenate
from tensorflow.keras.regularizers import l2
from tensorflow.keras.constraints import max_norm
from tensorflow.keras.models import Model

def residual_block(inputs, num_filters, kernel_size, strides, dilation_rate):
    x = Conv1D(num_filters, kernel_size=kernel_size, strides=strides, padding='same', dilation_rate=dilation_rate, use_bias=False)(inputs)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Conv1D(num_filters, kernel_size=kernel_size, strides=strides, padding='same', dilation_rate=dilation_rate, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = concatenate([inputs, x], axis=-1)
    x = Activation('relu')(x)
    return x

def inception_block(inputs, num_filters):
    tower_1 = Conv1D(num_filters, kernel_size=1, padding='same', use_bias=False)(inputs)
    tower_1 = BatchNormalization()(tower_1)
    tower_1 = Activation('relu')(tower_1)
    
    tower_2 = Conv1D(num_filters, kernel_size=1, padding='same', use_bias=False)(inputs)
    tower_2 = BatchNormalization()(tower_2)
    tower_2 = Activation('relu')(tower_2)
    tower_2 = Conv1D(num_filters, kernel_size=3, padding='same', use_bias=False)(tower_2)
    tower_2 = BatchNormalization()(tower_2)
    tower_2 = Activation('relu')(tower_2)
    
    tower_3 = Conv1D(num_filters, kernel_size=1, padding='same', use_bias=False)(inputs)
    tower_3 = BatchNormalization()(tower_3)
    tower_3 = Activation('relu')(tower_3)
    tower_3 = Conv1D(num_filters, kernel_size=5, padding='same', use_bias=False)(tower_3)
    tower_3 = BatchNormalization()(tower_3)
    tower_3 = Activation('relu')(tower_3)
    
    tower_4 = MaxPooling1D(pool_size=3, strides=1, padding='same')(inputs)
    tower_4 = Conv1D(num_filters, kernel_size=1, padding='same', use_bias=False)(tower_4)
    tower_4 = BatchNormalization()(tower_4)
    tower_4 = Activation('relu')(tower_4)
    
    output = concatenate([tower_1, tower_2, tower_3, tower_4], axis=-1)
    output = Activation('relu')(output)
    return output

def EEGNet(nb_classes, Samples=888, dropoutRate=0.5, kernLength=64, F1=8, D=2, F2=16, norm_rate=0.25, dropoutType='Dropout'):
    input1 = Input(shape=(Samples, 1))

    block1 = Conv1D(F1, kernLength, padding='same',
                    input_shape=(Samples, 1),
                    use_bias=False)(input1)
    block1 = BatchNormalization()(block1)
    block1 = DepthwiseConv1D(kernLength, use_bias=False,
                            depth_multiplier=D,
                            depthwise_constraint=max_norm(1.))(block1)
    block1 = BatchNormalization()(block1)
    block1 = Activation('relu')(block1)

    block1 = MaxPooling1D(pool_size=4)(block1)
    block1 = Dropout(dropoutRate)(block1)

    block2 = inception_block(block1, F2)
    block2 = MaxPooling1D(pool_size=4)(block2)
    block2 = Dropout(dropoutRate)(block2)

    block3 = residual_block(block2, num_filters=F2, kernel_size=kernLength,
                            strides=1, dilation_rate=1)
    block3 = residual_block(block3, num_filters=F2, kernel_size=kernLength,
                            strides=1, dilation_rate=1)
    block3 = residual_block(block3, num_filters=F2, kernel_size=kernLength,
                            strides=1, dilation_rate=1)
    block3 = MaxPooling1D(pool_size=4)(block3)
    block3 = Dropout(dropoutRate)(block3)

    flatten = SeparableConv1D(2*F2, kernel_size=1, activation='relu',
                            kernel_constraint=max_norm(norm_rate))(block3)
    flatten = Dropout(dropoutRate)(flatten)
    flatten = SeparableConv1D(4*F2, kernel_size=1, activation='relu',
                            kernel_constraint=max_norm(norm_rate))(flatten)
    flatten = Dropout(dropoutRate)(flatten)
    flatten = Flatten()(flatten)

    output = Dense(11, kernel_initializer='he_normal', activation='softmax')(flatten)
    model = Model(inputs=input1, outputs=output)
    return model

EEGModel = EEGNet(nb_classes = 11)

from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import categorical_crossentropy

optimizer = Adam()

EEGModel.compile(optimizer=optimizer, loss=categorical_crossentropy, metrics=['accuracy'])

history = EEGModel.fit(X_train, y_train, batch_size=128, epochs=100, validation_data=(X_val, y_val))

def plot_loss_curves(history):
    """
    Returns separate loss curves for training and validation metrics.
    """ 
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    accuracy = history.history['accuracy']
    val_accuracy = history.history['val_accuracy']

    epochs = range(len(history.history['loss']))

    # Plot loss
    plt.plot(epochs, loss, label='training_loss')
    plt.plot(epochs, val_loss, label='val_loss')
    plt.title('Loss')
    plt.xlabel('Epochs')
    plt.legend()

    # Plot accuracy
    plt.figure()
    plt.plot(epochs, accuracy, label='training_accuracy')
    plt.plot(epochs, val_accuracy, label='val_accuracy')
    plt.title('Accuracy')
    plt.xlabel('Epochs')
    plt.legend();

plot_loss_curves(history)

X_train.shape, X_val.shape

y_val.shape, y_train.shape

from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc

n_splits = 5


kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
k_fold_history = []

def EEGNet_to_history(X_train_fold, y_train_fold, X_val_fold, y_val_fold):
    
    model = EEGNet(nb_classes = 11)
    model.compile(loss=categorical_crossentropy, optimizer='adam', metrics=['accuracy',Precision(), Recall()])

    history = model.fit(X_train_fold, y_train_fold, epochs=30, batch_size=128, validation_data=(X_val_fold, y_val_fold), verbose=0)    

    return history

for train_idx, val_idx in kf.split(X_train):
    X_train_fold, y_train_fold = X_train[train_idx], y_train[train_idx]
    X_val_fold, y_val_fold = X_train[val_idx], y_train[val_idx]
    
    k_fold_history.append(EEGNet_to_history(X_train_fold, y_train_fold, X_val_fold, y_val_fold))

k_fold_history

def history_to_results(k_fold_history):
    loss = 0
    accuracy = 0
    precision = 0
    recall = 0
    val_loss = 0
    val_accuracy = 0
    val_precision = 0
    val_recall = 0
    for his in k_fold_history:
        his = his.history
        for key in his:
            if(key == 'loss'): loss += his[key][-1]
            if(key == 'accuracy'): accuracy += his[key][-1]
            if(key[:9] == 'precision'): precision += his[key][-1]
            if(key[:6] == 'recall'): recall += his[key][-1]
            if(key == 'val_loss'): val_loss += his[key][-1]
            if(key == 'val_accuracy'): val_accuracy += his[key][-1]
            if(key[:13] == 'val_precision'): val_precision += his[key][-1]
            if(key[:10] == 'val_recall'): val_recall += his[key][-1]
    print('loss', round(loss/5, 4))
    print('accuracy', round(accuracy/5, 4))
    print('precision', round(precision/5, 4))
    print('recall', round(recall/5, 4))
    print('F1 score', round(((2*(recall/5)*(precision/5))/((recall/5) + (precision/5))), 6))
    print('val_loss', round(val_loss/5, 4))
    print('val_accuracy', round(val_accuracy/5, 4))
    print('val_precision', round(val_precision/5, 4))
    print('val_recall', round(val_recall/5, 4))
    print('F1 score Validation', round((2*(val_recall/5)*(val_precision/5))/((val_recall/5) + (val_precision/5)), 4))

history_to_results(k_fold_history)





