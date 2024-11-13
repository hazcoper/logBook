"""
This script will be used to add extra fields to previous generated jsons
They will start as empty fields
This is to make sure that old jsons can be updated
"""


from common import get_json_list, load_data, dump_data



if __name__ == "__main__":
    
    field_name = "cutted"
    dict_location = "event_list"
    
    # get the list of jsons
    _, json_folder_list = get_json_list()
    
    for json_file_path in json_folder_list:
        print(json_file_path)
        
        data = load_data(json_file_path)
        
        # check if the field is already present
        if field_name in data[dict_location][0]:
            print("  Field already present, skipping")
            continue
        
        if dict_location == "":
            # means that it is in the root of the dictionary
            print(f"  Adding field to root {field_name}")
            data[field_name] = ""
        else:
            # means that it is in the event list
            
            # add the field to each event
            for evn in data[dict_location]:
                print(f"   Adding field to event {field_name}")
                evn[field_name] = ""
        
        # have finished changing this passage
        print("  Finished changing this passage, saving dict")
        
        dump_data(data, json_file_path)