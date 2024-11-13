"""
This will store some common features that will be used by the tools
"""
import json
import os

def get_json_list(json_folder="passage_metadata"):
    """
    Given a folder, it will return a list of all the json files in that folder
    a list with just the name and a list with the full path
    """
    
    json_list = [x for x in os.listdir(json_folder) if x.endswith(".json")]
    json_path_list = [os.path.join(json_folder, x) for x in json_list]

    return json_list, json_path_list

def load_data(json_file_path):
    """
    Gets the file path related to a certain passage, will load the file and return a dictionary
    """
    
    try:
        with open(json_file_path, "r") as file:
            data = json.load(file)
    except Exception as E:
        print(f"[ERROR] - load_data {json_file_path} - {E}")
        return {}
    return data

def dump_data(data, json_file_path):
    """
    Give a data dictionary and a file path. It will dump the dictioanry into the file path
    return true if it was succesfull false otherwise
    """
    
    try:
        with open(json_file_path, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as E:
        print(f"[ERROR] - dump_data {json_file_path} - {E}")
        return False

    return True

def check_elapsed_time(data_dict):
    """
    Receives a dictionary that was loaded from the json passages
    it will check if the elapsed time is present
    returns true when it is present, false otherwise

    need to check that every event in event list has it present
    """
    
    for evn in data_dict["event_list"]:
        if "elapsed_time" not in evn:
            return False
    
    return True