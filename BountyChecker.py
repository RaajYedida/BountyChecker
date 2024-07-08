import logging
import os
import time
import tkinter as tk
#import pyttsx3
import json
import threading
import requests
import json


def setup_custom_logger(name):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


class OverlayApp:
    def __init__(self):
        self.path = None
        self.root = tk.Tk()
        self.root.overrideredirect(True)  
        self.root.attributes("-topmost", True) 
        self.root.geometry("10x10")
        self.root.configure(bg='black')
        self.root.attributes("-alpha", 0.5) 
        self.enable_overlay = True
        self.label = tk.Label(self.root, text="Drag me around", fg="white", bg="black",
                              font=('Times New Roman', 15, ''))
        self.label.pack(fill="both", expand=True)
       
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<ButtonRelease-1>", self.stop_drag)
        self.label.bind("<B1-Motion>", self.on_drag)

        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

        self.logger = setup_custom_logger('Aya Bounty Tracker')
        
        self.path = os.path.expanduser('~/Library/Application Support/CrossOver/Bottles/Warframe Steam/drive_c/users/crossover/AppData/Local/Warframe/EE.log')
        self.first_run = True
        self.last_line_index = 0
        wanted_bounties = requests.get("https://gist.githubusercontent.com/ManInTheWallPog/d9cc2c83379a74ef57f0407b0d84d9b2/raw/")
        wanted_bounties = wanted_bounties.content
        bounty_translation = requests.get("https://gist.githubusercontent.com/ManInTheWallPog/02dfd3efdd62ed5b7061dd2e62324fa3/raw/")    
        bounty_translation = bounty_translation.content
        wanted_bounties_str = wanted_bounties.decode('utf-8')
        bounty_translation_str = bounty_translation.decode('utf-8')
        self.wanted_bounties = json.loads(wanted_bounties_str)
        self.bounty_translation = json.loads(bounty_translation_str)
        
    def start_drag(self, event):
        self.dragging = True
        self.offset_x = event.x
        self.offset_y = event.y

    def stop_drag(self, _):
        self.dragging = False

    def on_drag(self, event):
        if self.dragging:
            x = self.root.winfo_pointerx() - self.offset_x
            y = self.root.winfo_pointery() - self.offset_y
            self.root.geometry(f"+{x}+{y}")

    def update_overlay(self, text, text_color):
        self.label.config(text=text, fg=text_color)
        self.root.update_idletasks()
        width = self.label.winfo_reqwidth() + 2  # Add some padding
        self.root.geometry(f"{width}x40")

    def run(self):
        overlayselection = False
        while overlayselection == False:
            overlay_enabled = input("Do you want to enable Overlay? (Y/N):")
            overlay_enabled = overlay_enabled.replace("Yes", "Y").replace("No", "N").replace("y", "Y").replace("n", "N")
            if overlay_enabled == "Y":
                overlayselection = True
            elif overlay_enabled == "N":
                overlayselection = True
                self.enable_overlay = False
                self.root.attributes("-alpha", 0.0)
        threading.Thread(target=self.data_parser).start()
        self.update_overlay("starting", "white")
        self.root.mainloop()
        
            

    def data_parser(self):
        last_access = 0
        last_line_index  = 0
        
        #tts = pyttsx3.init()
        while True:
            try:
                checkaccesstime = os.path.getmtime(self.path)
                if checkaccesstime != last_access:
                    last_access = checkaccesstime
                    try:
                        data, current_last_index = self.read_ee(last_line_index)
                        if data == []:
                            continue
                    except Exception as e:
                        self.logger.info(f"Error reading EE.log {e}")
                        continue
                    if self.first_run:
                        self.first_run = False
                        text = "Waiting for bounty"
                        self.update_overlay(text, "white")
                        #tts.say(text)
                        #tts.runAndWait()
                        
                        with open(self.path, 'r', encoding="utf-8") as f:
                            lines = f.readlines()
                            for line in lines:
                                last_line_index = f.tell()
                        continue
                    parse_success = self.parse_lines(data)
                    if parse_success:
                        last_line_index = current_last_index
                time.sleep(0.5)
            except Exception as e:
                self.logger.info(f"Error reading EE.log {e}")
                time.sleep(0.5)

    def lstring(self, data, seperators):
        output = []
        var = ''
        for char in data:
            Outputting = True
            if char in seperators:
                Outputting = False
            if Outputting:
                var = var + char
            else:
                output.append(var)
                var = ''
        output.append(var)

        return output

    def read_ee(self, last_line_index):
        current_last_index = last_line_index
        with open(self.path, 'r', encoding="utf-8") as f:
            f.seek(current_last_index)
            lines = f.readlines()
            for line in lines:
                current_last_index = f.tell()
        return lines, current_last_index

    def parse_lines(self, data):  # Removed tts parameter
        for i in range(len(data)):
            line_data = self.lstring(data[i], ' ')
            try:
                if ' '.join(line_data[1:6]) == 'Net [Info]: Set squad mission:':
                    try:
                        data_string = ' '.join(line_data[6:])
                        json_start_index = data_string.find("{")
                        json_end_index = data_string.rfind("}") + 1
                        json_data = data_string[json_start_index:json_end_index]
                        json_data = json_data.replace('null', 'None').replace('true', 'True').replace('false', 'False').replace("True", '"True"')
                        try:
                            json_data = json.loads(json_data)
                        except Exception as e:
                            continue
                        
                        if not all(key in json_data for key in ['jobTier', 'jobStages', 'job']):
                            continue
                        if json_data.get("isHardJob") == "True":
                            self.update_overlay("Wrong Tier", "red")
                            text = "Wrong tier, Bounty is Steel Path"
                            #tts.say(text)
                            #tts.runAndWait()
                            return True

                        if json_data['jobTier'] != 4:
                            self.update_overlay("Wrong Tier", "red")
                            text = (f"Wrong tier, tier is {str(json_data['jobTier'])}")
                            #tts.say(text)
                            #tts.runAndWait()

                            return True

                        if not all(stage in self.wanted_bounties for stage in json_data['jobStages']):
                            try:
                                stages = [self.bounty_translation[stage] for stage in json_data['jobStages']]
                                stages_string = " -> ".join(stages)
                                self.logger.info(stages_string)
                                self.update_overlay(stages_string, "red")
                                self.logger.info("Bad Bounty")
                                #tts.say("Bad Bounty")
                                #tts.runAndWait()
                                return True
                            except Exception as e:
                                self.logger.error(f"Please Report this String: {e}")

                            return True
                    except Exception as e:
                        return False
                    stages = [self.bounty_translation[stage] for stage in json_data['jobStages']]
                    stages_string = " -> ".join(stages)
                    self.update_overlay(stages_string, "green")
                    self.logger.info(stages_string)
                    self.logger.info("Good Bounty")
                    #tts.say("Good Bounty")
                    #tts.runAndWait()
                    return True

            except Exception as e:
                continue

if __name__ == "__main__":
    
    app = OverlayApp()
    app.run()
    