import pickle
import json
import numpy as np
import pandas as pd
import azureml.train.automl
from sklearn.externals import joblib
from azureml.core.model import Model

def init():
    global model
    model_path = Model.get_model_path(model_name = 'AutoMLb2904534a8')
    # deserialize the model file back into a sklearn model
    model = joblib.load(model_path)
    
def unpack_message(raw_data):
    message_data = json.loads(raw_data)
    # convert single message to list 
    if type(message_data) is dict:
        message_data = [message_data]
    return message_data
    
def extract_features(message_data):
    X_data = []
    sensor_names = ['Sensor'+str(i) for i in range(1,22)]
    
    for message in message_data:
        # select sensor data from the message dictionary
        feature_dict = {k: message[k] for k in (sensor_names)}
        X_data.append(feature_dict)
    
    X_df = pd.DataFrame(X_data)
    return np.array(X_df[sensor_names].values)

def append_predict_data(message_data, y_hat):
    message_df = pd.DataFrame(message_data)
    message_df['PredictedRul'] = y_hat
    return message_df.to_dict('records')

def log_for_debug(log_message, log_data):
    print("*****%s:" % log_message)
    print(log_data)
    print("******")

def run(raw_data):
    log_for_debug("raw_data", raw_data)
    
    message_data = unpack_message(raw_data)
    log_for_debug("message_data", message_data)
    
    X_data = extract_features(message_data)
    log_for_debug("X_data", X_data)
   
    # make prediction
    y_hat = model.predict(X_data)
    
    response_data = append_predict_data(message_data, y_hat)
    return response_data
