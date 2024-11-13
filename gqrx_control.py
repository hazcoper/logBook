from xmlrpc.server import SimpleXMLRPCServer

import socket
import time

"""
The idea of this file is to create a class that will handle the connection and communication with gqrx
It will allow to easily send commands to send and recevie commands from the gqrx server
"""


class Gqrx:
    
    def __init__(self, host_list, port_list):
        """
        Receives host list and port list, the order is [gqrx, rpc_server]
        """
        self.gqrx_ip = host_list[0]
        self.gqrx_port = port_list[0]
        
        self.socket = None
        self.isConnected = True
    
        self.server = SimpleXMLRPCServer((host_list[1], port_list[1]))
        self.registerFunctions()
    
    def registerFunctions(self):
        """
        Register the functions available to the server
        """
        # for now i am only exposing this function
        # but in the future i should expose other functions as well
        self.server.register_function(self.get_radio_info)
    
    def startConnection(self):
        """
        Will start a connection to the gqrx server
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.gqrx_ip, self.gqrx_port))
            self.isConnected = True
            return True
        except Exception as e:
            print("Error in startConnection: ", e)
            self.isConnected = False
            return False
    
    def stopConnection(self):
        """
        Will stop the connection to the gqrx server
        """
        try:
            self.socket.close()
            self.isConnected = False
            return True
        except Exception as e:
            print("Error in stopConnection: ", e)
            return False

    def get_dbfs(self):
        """
        Will get the dbfs value from the gqrx server
        """
        try:
            self.socket.send("l STRENGTH\n".encode())
            data = self.socket.recv(1024)
            print("Data: ", data)
            return float(data.decode())
        except Exception as E:
            print("Error getting dbfs: ", E)
            return None
    
    def get_frequency(self):
        """
        Will get the frequency value from the gqrx server
        """
        try:
            self.socket.send("f\n".encode())
            data = self.socket.recv(1024)
            return float(data.decode())
        except Exception as E:
            print("Error getting frequency: ", E)
            return None
    
    def get_demodulator_mode(self):
        """
        Will get the demodulator mode from the gqrx server
        """
        try:
            self.socket.send("m\n".encode())
            data = self.socket.recv(1024)
            return data.decode()
        except Exception as E:
            print("Error getting demodulator mode: ", E)
            return None
    
    def get_squelch_threshold(self):
        """
        Will get the squelch threshold from the gqrx server
        """
        try:
            self.socket.send("l SQL\n".encode())
            data = self.socket.recv(1024)
            return float(data.decode())
        except Exception as E:
            print("Error getting squelch threshold: ", E)
            return None
        
    def get_iqrecording_status(self):
        """
        will get the status of the iq recorder
        """
        
        try:
            self.socket.send("u IQRECORD\n".encode())
            data = self.socket.recv(1024)
            return bool(int(data.decode()))
        except Exception as E:
            print("Error getting iq recording status: ", E)
            return None
    

    def get_gain(self):
        """
        Will get the gain from the gqrx server
        """
        try:
            self.socket.send("l PGA_GAIN GAIN\n".encode())
            data = self.socket.recv(1024)
            return data.decode()
        except Exception as E:
            print("Error getting gain: ", E)
            return None
        
    def get_radio_info(self):
        """
        General function that will call all available get methods and return the data as a dictionary
        this function is exposed to the outside world via xmlrpc
        """
        print("Getting radio info")
        function_list = [f for f in dir(self) if callable(getattr(self, f)) and f.startswith("get_") and f != "get_radio_info"]
        
        try:
            response_dict = {}
            for f in function_list:
                variable_name = f.split("get_")[1]
                response_dict[variable_name] = getattr(self, f)()
            print("  Radio info: ", response_dict)
            return response_dict
        except Exception as E:
            print("Error getting radio info: ", E)
            return {}
        
    def start_iq_recording(self):
        """
        Will start the recording of the IQ data
        """
        print("Will start IQ recording")
        try:
            self.socket.send("U IQRECORD 1\n".encode())
            data = self.socket.recv(1024)
            print("Reponse: ", data)
            return True
        except Exception as E:
            print("Error starting IQ recording: ", E)
            return False
    
    def stop_iq_recording(self):
        """
        Will stop the recording of the IQ data
        """
        print("Will stop IQ recording")
        try:
            self.socket.send("U IQRECORD 0\n".encode())
            data = self.socket.recv(1024)
            print("Reponse: ", data)
            return True
        except Exception as E:
            print("Error stopping IQ recording: ", E)
            return False


    
if __name__ == "__main__":
    
    gqrx_ip = "172.20.38.70"
    gqrx_ip = "localhost"
    gqrx_port = 7356
    
    rpc_ip = "localhost"
    rpc_port = 1712
    
    host_list = [gqrx_ip, rpc_ip]
    port_list = [gqrx_port, rpc_port]
    
    my_gqrx = Gqrx(host_list, port_list)
    my_gqrx.startConnection()
    

    # my_gqrx.get_dbfs()    

    my_gqrx.server.serve_forever()