import tkinter as tk
from datetime import datetime, timedelta
import random
import atexit
import signal
import xmlrpc.client


from data import MetaData, Event
from config_parser import ConfigParser


class Ui:
    def __init__(self):
        
        # load the configuration class
        self.config = ConfigParser()
        self.config.loadConfig()
        
        # rpc proxy to send the events
        self.proxy = xmlrpc.client.ServerProxy(f"http://{self.config.get('manager_rpc_host')}:{self.config.get('manager_rpc_port')}/")


        # these are all configs that should be loaded from a config file
        # Signal intervals in seconds
        self.SIGNALS = ["AFSK", "Beacon", "Long Beacon"]    # this should be just a single dictionary and not two separate variables
        self.INTERVALS = {
            "AFSK": 120,         # 2 minutes
            "Beacon": 60,        # 1 minute
            "Long Beacon": 300   # 5 minutes
        }

        # Event colors for actual and expected events and buttons
        self.EVENT_COLORS = {
            "AFSK": ("#ff9933", "#ffcc99"),  # Orange for actual, light orange for expected
            "Beacon": ("#0066ff", "#99ccff"),  # Blue for actual, light blue for expected
            "Long Beacon": ("#8a2be2", "#dab6ff")  # Violet for actual, light violet for expected
        }

        self.BUTTON_COLORS = {
            "AFSK": "#ff9933",    # Orange
            "Beacon": "#0066ff",  # Blue
            "Long Beacon": "#8a2be2"  # Violet
        }

        # Define the fixed timeline window of 15 minutes
        self.TIMELINE_DURATION = 13 * 60  # 13 minutes in seconds
        self.CANVAS_WIDTH = 900  # Canvas width in pixels
        self.TIMELINE_HEIGHT = 50  # Canvas height in pixels


        # GeneralPurpose variables
        self.countdowns = {signal: 0 for signal in self.INTERVALS}
        self.is_recording = False
        self.recording_start_time = None
        self.timeline_events = []
        
        
        self.create_ui()
        
        
    # create the ui
    def create_ui(self):
        self.app = tk.Tk()
        self.app.title("ISTSAT1 Operations UI")
        
        # Status label to display recording info at the top
        self.status_label = tk.Label(self.app, text="Waiting to start recording...", font=("Helvetica", 12), pady=10, bg="green", fg="white")
        self.status_label.pack(fill="x")
        
        # Recording duration label below status label
        self.recording_duration_label = tk.Label(self.app, text="Recording Duration: 00:00", font=("Helvetica", 12), pady=5)
        self.recording_duration_label.pack()
        
        # Main frame to organize left and right sections
        self.main_frame = tk.Frame(self.app)
        self.main_frame.pack(fill="both", expand=True)
        
        # Left frame for buttons, centered vertically
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side="left", fill="y", expand=True)
        
        # Button to start and stop recording, centered in the left half
        self.start_button = tk.Button(self.left_frame, text="Start Recording", command=self.startRecording, height=2, width=20, bg="green", fg="black")
        self.start_button.pack(pady=5)
        
        # Signal detection buttons with specified colors, also centered in the left half
        for signal in self.SIGNALS:
            button = tk.Button(self.left_frame, text=f"{signal} Signal", command=lambda sig=signal: self.markSignal(sig), height=2, width=20, bg=self.BUTTON_COLORS[signal], fg="white")
            # change text color to black
            button.config(fg="black")
            button.pack(pady=5)
            
        # Right frame for signal information, centered on the right half of the screen
        self.right_frame = tk.Frame(self.main_frame, width=250, height=200)
        self.right_frame.pack(side="right", fill="y", expand=True)
        self.right_frame.pack_propagate(False)
        
        # Signal information label with a fixed width and height to prevent button shifting
        self.info_label = tk.Label(self.right_frame, text="No signal detected yet.", font=("Helvetica", 12), anchor="center", justify="center", width=30, height=8, wraplength=250)
        self.info_label.pack(fill="both", expand=True)
        
        # Countdown frame centered below main_frame
        self.countdown_frame = tk.Frame(self.app)
        self.countdown_frame.pack(pady=10)
        
        # Table Header for countdown frame
        self.header_label = tk.Label(self.countdown_frame, text="Signal Type", font=("Helvetica", 10, "bold"), width=20)
        self.header_label.grid(row=0, column=0)
        self.time_label = tk.Label(self.countdown_frame, text="Next Event Countdown", font=("Helvetica", 10, "bold"), width=20)
        self.time_label.grid(row=0, column=1)
        
        # Countdown Labels for each signal type
        self.countdown_labels = {}
        for i, signal in enumerate(self.SIGNALS, start=1):
            signal_label = tk.Label(self.countdown_frame, text=signal, font=("Helvetica", 10))
            signal_label.grid(row=i, column=0)
            self.countdown_labels[signal] = tk.Label(self.countdown_frame, text="0s", font=("Helvetica", 10))
            self.countdown_labels[signal].grid(row=i, column=1)
        
        # Timeline canvas at the bottom of the main window
        self.timeline_canvas = tk.Canvas(self.app, width=self.CANVAS_WIDTH, height=self.TIMELINE_HEIGHT, bg="white")
        self.timeline_canvas.pack(pady=10)
        
            
    def resetCountdowns(self):
        self.countdowns = {signal: 0 for signal in self.INTERVALS}

        
    def updateCountdowns(self):
        for signal, label in self.countdown_labels.items():
            if self.countdowns[signal] > 0:
                self.countdowns[signal] -= 1
            label.config(text=f"{self.countdowns[signal]}s")
        self.app.after(1000, self.updateCountdowns)
        
    def updateCurrentTimeBar(self):
        if self.is_recording:
            elapsed_time = (datetime.now() - self.recording_start_time).total_seconds()
            x_pos = int(elapsed_time * self.CANVAS_WIDTH / self.TIMELINE_DURATION)
            self.timeline_canvas.delete("current_time_bar")
            if 0 <= elapsed_time <= self.TIMELINE_DURATION:
                self.timeline_canvas.create_line(x_pos, 0, x_pos, self.TIMELINE_HEIGHT, fill="red", width=2, tags="current_time_bar")
        self.app.after(1000, self.updateCurrentTimeBar)
        
    
    def addTimilineEvent(self, event_time, signal_type, event_type):
        if not self.is_recording:
            return
        event_bar_size = 2
        elapsed_time = (event_time - self.recording_start_time).total_seconds()
        if 0 <= elapsed_time <= self.TIMELINE_DURATION:
            x_pos = int(elapsed_time * self.CANVAS_WIDTH / self.TIMELINE_DURATION)
            color = self.EVENT_COLORS[signal_type][0] if event_type == "actual" else self.EVENT_COLORS[signal_type][1]
            self.timeline_canvas.create_rectangle(x_pos, 0, x_pos + event_bar_size, self.TIMELINE_HEIGHT, fill=color, outline="")
    
    # Function to mark signal detection and start countdown
    def markSignal(self, signal_type):
        global countdowns, timeline_events
        
        self.countdowns[signal_type] = self.INTERVALS[signal_type]
        print("Signal detected:", signal_type)
        
        # add current event to timeline
        self.addTimilineEvent(datetime.now(), signal_type, "actual")
        # add expected event to timeline
        self.addTimilineEvent(datetime.now() + timedelta(seconds=self.INTERVALS[signal_type]), signal_type, "expected")
        
        # register event with the manager
        self.proxy.registerEvent(signal_type)     # [check] - eventually should make these call async
        # signal_info = (
        #     f"Signal Type: {signal_type}\n"
        #     f"Time: {detection_time.strftime('%H:%M:%S')}\n"
        #     f"Frequency: {frequency / 1e6:.2f} MHz\n"
        #     f"Azimuth: {azimuth:.2f}°\n"
        #     f"Elevation: {elevation:.2f}°"
        # )
        
        self.info_label.config(text=f"Signal Type: {signal_type}\nTime: {datetime.now().strftime('%H:%M:%S')}")

    def startRecording(self):
        """
        Function that is called when start recording button is pressed
        it will change the button to stop recording, reset the countdowns to make sure that they are ready
        """
        
        # call remote method to start recording
        self.proxy.startRecording()    # [check] - eventually should make these call async
        
        self.resetCountdowns()
        self.is_recording = True
        self.recording_start_time = datetime.now()
        self.status_label.config(text="Recording...", bg="red")
        self.start_button.config(text="Stop Recording", command=self.stopRecording, bg="red", fg="white")
        self.updateRecordingDuration()

    def stopRecording(self):
        """
        Function that is called when stop recording button is pressed
        it will change the button to start recording, reset the countdowns to make sure that they are ready
        """
        
        # call remote method to stop recording
        self.proxy.stopRecording()    # [check] - eventually should make these call async
        
        self.is_recording = False
        self.status_label.config(text="Recording stopped", bg="green")
        self.start_button.config(text="Start Recording", command=self.startRecording, bg="green", fg="black")
        self.recording_duration_label.config(text="Recording Duration: 00:00")
        self.timeline_canvas.delete("all")
        self.timeline_events.clear()

    def updateRecordingDuration(self):
        if self.is_recording:
            elapsed_time = datetime.now() - self.recording_start_time
            minutes, seconds = divmod(elapsed_time.seconds, 60)
            self.recording_duration_label.config(text=f"Recording Duration: {minutes:02}:{seconds:02}")
            self.app.after(1000, self.updateRecordingDuration)



    def loop(self):
        self.updateCountdowns()
        self.updateCurrentTimeBar()
        self.app.mainloop()






if __name__ == "__main__":

    my_ui = Ui()
    while True:
        my_ui.loop()


# MY_METADATA = None    # actually the metadata is going to be handled by the manager and not by the ui

# # Function to ensure metadata is dumped on unexpected exit
# def cleanup_metadata_on_exit():
#     global MY_METADATA
#     if MY_METADATA:
#         # Stop recording and append "_stopped" to indicate abrupt termination
#         MY_METADATA.stop_recording(datetime.now())
#         MY_METADATA.dump(filename_suffix="_stopped")
#         MY_METADATA = None

    
# # Function to mark signal detection and start countdown
# def mark_signal(signal_type):

#     # create the new event object
#     if is_recording:
#         new_event = Event(signal_type, detection_time, frequency, azimuth, elevation)
#         print(new_event)
#         MY_METADATA.register_event(new_event)
        

# # Register cleanup_metadata_on_exit to be called at program exit
# atexit.register(cleanup_metadata_on_exit)

# # Register signal handlers to ensure cleanup on SIGINT and SIGTERM
# signal.signal(signal.SIGINT, lambda sig, frame: cleanup_metadata_on_exit() or exit(0))
# signal.signal(signal.SIGTERM, lambda sig, frame: cleanup_metadata_on_exit() or exit(0))
