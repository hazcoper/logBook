from xmlrpc.server import SimpleXMLRPCServer
import socket

"""
The idea of this file is to create a class that will handle the connection and communication with rotctld
It will allow to easily send commands to the controller and receive back information from the controller
"""

class RotCtl:
    """
    Class that will handle the connection and interface with rotctld
    Receives ip, port, max_azi, min_azi, max_ele, min_ele
    
    Will not send commands out of bounds
    
    Has the ability to send commands and to recevie them
        - setAzimuthElevation
        - getAzimuthElevation    
    """
    
    def __init__(self, host_list, port_list):
        """
        Receives host list and port list, the order is [rotctl, rpc_server]
        """
        self.rotctl_ip = host_list[0]
        self.rotctl_port = port_list[0]
        
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
        self.server.register_function(self.get_rotctl_info)

    def startConnection(self):
        """
        Will start a connection to the rotctld server
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.rotctl_ip, self.rotctl_port))
            return True
        except Exception as e:
            print("Error in startConnection: ", e)
            return False
    
    def stopConnection(self):
        """
        Will stop the connection to the rotctld server
        """
        try:
            self.socket.close()
            return True
        except Exception as e:
            print("Error in stopConnection: ", e)
            return False
        
        
    def setAzimuthElevation(self, azimuth, elevation):
        """
        Will send the command to the rotctld to set the azimuth and elevation
        """
        try:
            
            if not self.isConnected:
                print("Not connected to rotctld")
                return False
        
            if azimuth < self.min_azi or azimuth > self.max_azi:
                print("Azimuth out of bounds")
                return False
            
            if elevation < self.min_ele or elevation > self.max_ele:
                print("Elevation out of bounds")
                return False
            
            command = f"P {azimuth} {elevation}\n"
            self.socket.sendall(command.encode())
            return True
        except Exception as e:
            print("Error in setAzimuthElevation: ", e)
            return False
        
    
    def getAzimuthElevation(self):
        """
        Will send the command to the rotctld to get the azimuth and elevation
        """
        try:
            
            if not self.isConnected:
                print("Not connected to rotctld")
                return None, None
        
            command = "p\n"
            self.socket.sendall(command.encode())
            data = self.socket.recv(1024).decode()
            data = data.split("\n")[:-1]
            azimuth = float(data[0])
            elevation = float(data[1])
            return azimuth, elevation
        except Exception as e:
            print("Error in getAzimuthElevation: ", e)
            return None, None
        
    def get_rotctl_info(self):
        """
        Function exposed to the outside world to get the rotctl info
        """
        print("Getting rotctl info")
        
        azimuth, elevation = self.getAzimuthElevation()
        output_dict = {"azimuth": azimuth, "elevation": elevation}

        print("  rotctl info: ", output_dict)
        
        return output_dict

def main():
    
    import time
    
    # Connect to the rigctld rotator control server
    rotctl_ip = "172.20.38.211"
    # rotctl_ip = "localhost"
    rotctl_port = 4533

    rpc_server_ip = "localhost"
    rpc_server_port = 1713 
    
    host_list = [rotctl_ip, rpc_server_ip]
    port_list = [rotctl_port, rpc_server_port]
    
    my_rot = RotCtl(host_list, port_list)
    my_rot.startConnection()
    
    my_rot.server.serve_forever()
    
    my_rot.stopConnection()
    
if __name__ == "__main__":
    main()
