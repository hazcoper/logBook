"""
Elapsed time was a feature that was added recently
there are some passages that have been recorded without this feature

this script will go over all the jsons, check if they have the elapsed time
    if not, it will add the elapsed time
        see the difference between the time and start record time    
elapsed time is in format mm:ss

assuming that we are running this file from the repo root folder
"""

import json
import datetime

from common import get_json_list, check_elapsed_time, load_data, dump_data

if __name__ == "__main__":
    
    _, json_folder_list = get_json_list()


    for json_file_path in json_folder_list:
        print(json_file_path)
        
        data = load_data(json_file_path)
        
        if check_elapsed_time(data):
            print("  Elapsed time present, skipping")
            continue


        # means that elapsed time is not present, lets calculate it and add to each event
        # start_time = datetime.datetime.strptime(data["start_record_time"], "%Y_%m_%d_%H-%M-%S")
        start_time = datetime.datetime.fromisoformat(data["start_record_time"])
        print("  Start  time: ", start_time)
        for evn in data["event_list"]:
            event_time = datetime.datetime.fromisoformat(evn["time"])
            
            elapsed_time = event_time - start_time

            total_seconds = int(elapsed_time.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            elapsed_time_str = f"{minutes:02}:{seconds:02}"
            
            print("    Event time: ", event_time)
            print("     Elapsed time: ", elapsed_time)
            print("     Elapsed string: ", elapsed_time_str)
            
            evn["elapsed_time"] = elapsed_time_str
            
        # have finished changing this passage
        print("  Finished changing this passage, saving dict")
        
        dump_data(data, json_file_path)
            