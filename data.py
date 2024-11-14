import os
import json
from datetime import datetime

class Event:
    """
    This is the class that will be responsible for representing an event.
    It supports all types of events.
    
    This class should contain no logic, it is just to store data
    But it should have a method to convert the object into a dictionary for JSON serialization
    """
    
    def __init__(self, name, time, elapsed_str, freq, gain, azimuth, elevation, extra_data={}):
        """
        name : str
            The name of the event
        time : datetime
            The time when the event happened
        elapsed_str : str
            The time elapsed since the start of the recording in the format "mm:ss"
        freq : str
            Current gqrx selected frequency
        gain : str
            Current gqrx selected gain
        azimuth : str
            Current rotctl azimuth
        elevation : str
            Current rotctl elevation
        extra_data : dict
            Any other data that might be needed
        """
        
        if not isinstance(name, str):
            raise ValueError(f"Event creation name {name} must be a string")

        if not isinstance(time, datetime):
            raise ValueError(f"Event creation time {time} must be a datetime object")
        
        if not isinstance(elapsed_str, str):
            raise ValueError(f"Event creation elapsed_str {elapsed_str} must be a string")
        
        if not isinstance(freq, float):
            raise ValueError(f"Event creation freq {freq} must be a string")
        
        if not isinstance(gain, str):
            raise ValueError(f"Event creation gain {gain} must be a string")

        if not isinstance(azimuth, float):
            raise ValueError(f"Event creation azimuth {azimuth} must be a string")
    
        if not isinstance(elevation, float):
            raise ValueError(f"Event creation elevation {elevation} must be a string")
        
        if not isinstance(extra_data, dict):
            raise ValueError(f"Event creation extra_data {extra_data} must be a dictionary")
        
        # check that all the data in the extra data is a string, int or float
        for key in extra_data:
            if not isinstance(extra_data[key], str) and not isinstance(extra_data[key], int) and not isinstance(extra_data[key], float):
                raise ValueError(f"Extra data {extra_data[key]} must be a string, int or float")
                
        # check to see if time is the correct type
        self.name = name
        self.time = time
        self.elapsed_str = elapsed_str
        self.freq = freq
        self.gain = gain
        self.azimuth = azimuth
        self.elevation = elevation
        self.extra_data = extra_data   # a dictionary with any other extra data that might eventually be needed
    
    def __str__(self):
        return f"{self.name} at {self.time} on {self.freq} with azimuth {self.azimuth} and elevation {self.elevation}"

    def to_dict(self):
        """
        Convert the Event object into a dictionary for JSON serialization.
        """
        return {
            "name": self.name,
            "time": self.time.isoformat(),
            "elapsed_time": self.elapsed_str,
            "freq": self.freq,
            "azimuth": self.azimuth,
            "elevation": self.elevation,
            "extra_data": self.extra_data
        }

class MetaData:
    """
    This will be the class responsible for storing all the metadata during the passage.
    It will have methods to dump that metadata into a file for later use.
    """
    
    def __init__(self):
        """
        All time values are expected to be datetime objects.
        They will be converted to text by this module
        """
        self.comment = None
        self.start_record_time = None
        self.end_record_time = None
        self.event_list = []       # This will be ordered by adding time
    
    def start_recording(self, current_time):
        """
        This method is responsible for marking the start of the recording.
        Should receive a datetime object
        """
        
        if not isinstance(current_time, datetime):
            raise ValueError(f"Start Recording time {current_time} must be a datetime object")
        
        self.start_record_time = current_time
        
    def stop_recording(self, current_time):
        """
        This method is responsible for marking the end of the recording.
        """
        if not isinstance(current_time, datetime):
            raise ValueError(f"Stop Recording time {current_time} must be a datetime object")

        self.end_record_time = current_time

    def register_event(self, event):
        """
        Given an event object, it will register it in the event list.
        Returns True if the event was successfully registered.
        """
        
        if not isinstance(event, Event):
            raise ValueError(f"Register event Event {event} must be an Event object")
        
        self.event_list.append(event)
        
        return True
    
    def dump(self, file_folder="passage_metadata", file_name="", filename_suffix=""):
        """
        This method will dump the metadata into a file.
        """
        try:

            date_string_format = "%Y_%m_%d_%H-%M-%S"
            start_time_file = self.start_record_time.strftime(date_string_format) if isinstance(self.start_record_time, datetime) else str(self.start_record_time)
            
            # Check if the file folder needs to be created
            if not os.path.exists(file_folder):
                os.makedirs(file_folder)
            
            # Check if the file name is provided, otherwise use start_record_time
            if not file_name:
                file_name = f"{start_time_file}.json"
                if filename_suffix:
                    file_name = f"{start_time_file}_{filename_suffix}.json"
                    
            file_path = os.path.join(file_folder, file_name)
            
            # Prepare the metadata dictionary to be serialized
            metadata_dict = {
                "comment": self.comment,
                "start_record_time": self.start_record_time.isoformat(),
                "end_record_time": self.end_record_time.isoformat(),
                "event_list": [event.to_dict() for event in self.event_list]  # Convert each event to dict
            }
            
            print(metadata_dict)
            
            # Dump the data
            with open(file_path, "w") as file:
                json.dump(metadata_dict, file, indent=4)
        
        except Exception as e:
            print("Error in dump: ", e)
            return False

        return True
        
            
if __name__ == "__main__":
    # This is just a test to see if the classes are working as expected
    meta = MetaData()
    print(meta.comment)
    print(meta.start_record_time)
    print(meta.event_list)
    
    event1 = Event("First event", datetime(2024, 11, 6, 12, 0), "123.123", "123", "123")
    event2 = Event("Second event", datetime(2024, 11, 6, 12, 1), "123.123", "123", "123")
    event3 = Event("Third event", datetime(2024, 11, 6, 12, 2), "123.123", "123", "123")
    
    meta.register_event(event1)
    meta.register_event(event2)
    meta.register_event(event3)
    meta.register_event("hello")
    
    for event in meta.event_list:
        print(event)
    
    print(meta.comment)
    print(meta.start_record_time)
    print(meta.event_list)
    
    # Now I should dump this into a file
    meta.dump()
