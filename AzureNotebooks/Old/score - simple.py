%%writefile $script_file_name
import json
import numpy as np
import pandas as pd
import azureml.train.automl
import joblib
from azureml.core.model import Model

def init():
    global model
    print(Model.get_model_path(model_name = '<<modelname>>'))
    model_path = Model.get_model_path(model_name = '<<modelname>>')
    # deserialize the model file back into a sklearn model
    model = joblib.load(model_path)
    
def unpack_message(raw_data):
    message_data = json.loads(raw_data)
    # convert single message to list 
    if type(message_data) is dict:
        message_data = [message_data]
    return message_data   

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