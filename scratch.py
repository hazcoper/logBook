import xmlrpc.client
from datetime import datetime
import time

from gqrx_control import Gqrx

# # Connect to the Manager server
# manager_proxy = xmlrpc.client.ServerProxy("http://localhost:1701/")

# # Prepare the event data
# event_name = "Test Event"
# event_datetime = datetime.now()

# # Call the registerEvent function
# try:
#     result = manager_proxy.registerEvent(event_name, event_datetime)
#     if result:
#         print("Event registered successfully!")
#     else:
#         print("Event registration failed.")
# except Exception as e:
#     print("Error calling registerEvent:", e)


"""
the problem is that when i connect to gqrx, it loses the connection with gpredict...
what I would like to have access in gqrx:
    - current selected frequency
    - radio gains
    - start recording

the current selected frequency, i could get from gpredict as well
    but that would be one extra step that i would have to do

i could change gqrx to add this feature
    support command to start raw recording
    support command to stop raw recording
    play raw file in loop
    support multiple sockets
"""

gqrx_ip = "172.20.38.70"
gqrx_ip = "localhost"
gqrx_port = 7356

rpc_ip = "localhost"
rpc_port = 1900

host_list = [gqrx_ip, rpc_ip]
port_list = [gqrx_port, rpc_port]

my_gqrx = Gqrx(host_list, port_list)    
my_gqrx.startConnection()

my_gqrx.get_radio_info()
print("Starting iq recording")
my_gqrx.start_iq_recording()
my_gqrx.get_radio_info()
time.sleep(10)
print("Finishing iq recording")
my_gqrx.stop_iq_recording()
my_gqrx.get_radio_info()


