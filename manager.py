"""
This file will contain the manager class
It will be resposible for mangaging the interactions between the different parts of the system
It will implement a xml server that will receive the commands from the other parts
"""

from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from data import Event, MetaData
from datetime import datetime

from config_parser import ConfigParser

class Manager:
    
    def __init__(self):
        """
        It is expecting to receive the list in order for [server, gqrx, rotctl]
        """
        
        # load the configuration class
        self.config = ConfigParser()
        self.config.loadConfig()
        
        # Define the server with IP and port
        self.server = SimpleXMLRPCServer((self.config.get("manager_rpc_host"), self.config.get("manager_rpc_port")))
        self.registerFunctions()
        
        self.gqrx_proxy  = xmlrpc.client.ServerProxy(f"http://{self.config.get('gqrx_rpc_host')}:{self.config.get('gqrx_rpc_port')}")
        self.rotctl_proxy = xmlrpc.client.ServerProxy(f"http://{self.config.get('rotctl_rpc_host')}:{self.config.get('rotctl_rpc_port')}")
        
        
        self.meta_data = None     # this will be a object of the MetaData class
        # responsible for keeping track of all the data during a passage
        # it will be created once we start recording
        # and it wil be dumped into a file once we stop recording

        
    def registerFunctions(self):
        """
        Register the functions available to the server
        """
        self.server.register_function(self.registerEvent)   # this will be called by the ui class
        self.server.register_function(self.startRecording)  # this will be called by the ui class
        self.server.register_function(self.stopRecording)   # this will be called by the ui class
    
    def startRecording(self):
        """
        called by the ui to start recording
        Start the recording of the passage
        """
        
        current_time = datetime.now()  # this is the only time that i trust, the manager time
        
        # create a new metadata object
        self.meta_data = MetaData()
        
        # start the recording
        self.meta_data.start_recording(current_time)
        
        # should call gqrx start recording funciton, but it is still not implemented
        self.gqrx_proxy.start_recording()
                
        return True
    
    def stopRecording(self):
        """
        called by the ui to stop recording
        Stop the recording of the passage
        """
        
        self.gqrx_proxy.stop_recording()
        current_time = datetime.now()  # this is the only time that i trust, the manager time
        
        # stop the recording
        self.meta_data.stop_recording(current_time)
        
        # should call gqrx stop recording funciton, but it is still not implemented
        # [check] - implement gqrx stop recording function 
        
        # dump the metadata into a file
        print("Dumping metadata")
        self.meta_data.dump()
        self.meta_data = None
        return True
    
    def registerEvent(self, event):
        """
        called by the ui to register an event
        Register an event in the metadata
        """
        
        current_time = datetime.now()  # this is the only time that i trust, the manager time

        # get difference between current time and start time in mm:ss

        if self.meta_data is None:
            print("There is no metadata object. Please start recording first.")
            return False
    
        # need to query the gqrx and rotctl to get the required information to create the event
        # query gqrx for radio information. i am looking for a sort of snapshot of the radio
        try:
            print("Getting radio dict")
            radio_dict = self.gqrx_proxy.get_radio_info()         # this will return a dictionary with all the values that have been taken from the server         
            print("getting rotctl dict")
            rotctl_dict = self.rotctl_proxy.get_rotctl_info()     # this will return a dictionary with the azimuth and elevation
        except Exception as e:
            print("Error in registerEvent: ", e)
            return False

        # print("Radio dict: ", radio_dict)
        print("Rotctl dict: ", rotctl_dict)

        # get the main information
        azimuth = rotctl_dict["azimuth"]
        elevation = rotctl_dict["elevation"]
        freq = radio_dict["frequency"]
        gain = radio_dict["gain"]

        # remove the values from the dictionaries so we are only left with the extra data
        # del radio_dict["frequency"]
        del radio_dict["gain"]
        del rotctl_dict["azimuth"]
        del rotctl_dict["elevation"]
        
        elapsed_time = current_time - self.meta_data.start_record_time
        # transform time to string "mm:ss"
        total_seconds = int(elapsed_time.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        elapsed_time_str = f"{minutes:02}:{seconds:02}"
        
        my_event = Event(event, current_time, elapsed_time_str, freq, gain, azimuth, elevation, {**rotctl_dict})

        # register the event
        self.meta_data.register_event(my_event)

        print("Event received: ", event)
        print("  at time: ", current_time)
        return True
    
    def main(self):
        """
        This is the class that will be used for the code to run itself
        """
        self.server.serve_forever()
    

if __name__ == "__main__":
    
    manager = Manager()
    manager.server.serve_forever()