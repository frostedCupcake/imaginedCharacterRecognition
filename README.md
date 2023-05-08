# Imagined Character Recognition Using Deeplearning

Imaginary number prediction using EEG signals is a fascinating application of machine learning. In this research paper, we propose a deep learning model to recognize the imaginary number a subject is thinking about, based on their brainwave signals. We have used the Mind BigData open database, which contains 67,635 brain signals of 2 seconds each, captured with the stimulus of seeing a digit (from 0 to 9) and thinking about it. We have preprocessed the data by clipping all EEG data to 888 values and applied normalization and one-hot encoding to the labels. We have split the data into train, validation, and test sets and used a deep learning model with residual blocks and inception blocks for prediction. The model achieved an accuracy of 25.5% on the test set.

### Configuration 

First time:

```
cd model
virtualenv env
. env/bin/activate
pip install -r requirements.txt
```

#### Run the model

```
python3 model_train.py
```
