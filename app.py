import ctypes
import time
import threading
import psutil
from functools import partial
from tkinter import Tk, Label, Entry, Button, Checkbutton, StringVar, IntVar
from infi.systray import SysTrayIcon
from texts import TEXTS, update_texts

MB_ICONWARNING = 0x30
MB_SYSTEMMODAL = 0x1000

class on_off_check:
    def __init__(self, on_off):
        self.on_off = on_off

    def get(self):
        return self.on_off
    
    def turn_on(self):
        self.on_off = True

    def turn_off(self):
        self.on_off = False

class BatteryChecker:
    def __init__(self, flag, app_instance):
        self.check_battery_thread = None
        self.check_battery_flag = flag
        self.app = app_instance
    
    # Windows notification function
    def message_box(self, title, text):
        ctypes.windll.user32.MessageBoxW(0, title, text, MB_ICONWARNING | MB_SYSTEMMODAL)
    
    # Battery status check function
    def check_battery(self):
        while self.check_battery_flag.get():
            battery = psutil.sensors_battery()
            percent = battery.percent
            charging = battery.power_plugged

            if ((not charging and percent < float(self.app.min_battery.get())) or
               (charging and not self.app.disable_min_battery_alert_on_charging.get() and percent < float(self.app.min_battery.get())) or
               (charging and percent > float(self.app.max_battery.get())) or
               (not charging and not self.app.disable_max_battery_alert_on_discharging.get() and percent > float(self.app.max_battery.get()))):
                self.app.root.deiconify()
                self.message_box(TEXTS[self.app.current_language.get()]["warning"], 
                                 TEXTS[self.app.current_language.get()]["battery_status"].format(percent))

            for _ in range(int(self.app.alert_interval.get()) * 300):  # Check every 0.2 seconds during the alert interval
                if not self.check_battery_flag.get():  # If the termination flag is set, exit the function
                    return
                time.sleep(0.2)
    
    # Run the battery check thread
    def start_or_stop_check_battery_thread(self):
        if self.check_battery_thread is not None and self.check_battery_thread.is_alive():  # If the thread is already running, stop it
            self.check_battery_flag.turn_off()  # Set the termination flag
            self.check_battery_thread.join()  # Wait for the thread to terminate
            self.app.start_button.config(text=TEXTS[self.app.current_language.get()]["start"])  # Change the button text to 'start'
        else:  # If the thread is not running, start it
            self.app.settings_manager.write_settings()
            self.check_battery_flag.turn_on()  # Set the run flag for the new thread
            self.check_battery_thread = threading.Thread(target=self.check_battery)
            self.check_battery_thread.start()
            self.app.start_button.config(text=TEXTS[self.app.current_language.get()]["stop"])  # Change the button text to 'stop'

class SettingsManager:
    def __init__(self, app_instance):
        self.app = app_instance

    def read_settings(self):
        try:
            with open("settings.txt", "r") as file:
                self.app.max_battery.set(file.readline().strip())
                self.app.min_battery.set(file.readline().strip())
                self.app.alert_interval.set(file.readline().strip())
                self.app.disable_min_battery_alert_on_charging.set(int(file.readline().strip()))
                self.app.disable_max_battery_alert_on_discharging.set(int(file.readline().strip()))
                self.app.current_language.set(file.readline().strip())
        except FileNotFoundError:
            self.app.current_language.set("en")  # Set the default language to English if the file is not found

    # Write settings file function
    def write_settings(self):
        with open("settings.txt", "w") as file:
            file.write(self.app.max_battery.get() + "\n")
            file.write(self.app.min_battery.get() + "\n")
            file.write(self.app.alert_interval.get() + "\n")
            file.write(str(self.app.disable_min_battery_alert_on_charging.get()) + "\n")
            file.write(str(self.app.disable_max_battery_alert_on_discharging.get()) + "\n")
            file.write(self.app.current_language.get() + "\n")

class LanguageManager:
    def __init__(self, app_instance):
        self.app = app_instance
    
    # Change language function
    def change_language(self, new_language):
        self.app.current_language.set(new_language)
        self.app.settings_manager.write_settings()
        update_texts(self.app.labels, self.app.current_language.get())
        if self.app.battery_checker.check_battery_flag.get():
            print('Battery checker is on.')  # You can replace this line with the appropriate action.

class AppGUI:
    def __init__(self):
        # Tkinter GUI
        self.root = Tk()
        self.root.title("My Application")
        self.root.resizable(0, 0)  # disable window resizing

        # Variables
        self.current_language = StringVar()
        self.max_battery = StringVar()
        self.min_battery = StringVar()
        self.alert_interval = StringVar()
        self.disable_min_battery_alert_on_charging = IntVar()
        self.disable_max_battery_alert_on_discharging = IntVar()

        # Classes
        self.battery_checker = BatteryChecker(check_battery_flag, self)
        self.settings_manager = SettingsManager(self)
        self.language_manager = LanguageManager(self)

        # Read the saved settings at the start of the program
        self.settings_manager.read_settings()

        # Initialize the UI
        self.init_ui()

    def init_ui(self):
        # Create the label
        self.Label_max_battery = Label(self.root)
        self.Label_low_battery = Label(self.root)
        self.Label_Alert_interval = Label(self.root)

        self.Label_max_battery.grid(row=0, column=0)  # Position the label
        self.Label_low_battery.grid(row=1, column=0)  # Position the label
        self.Label_Alert_interval.grid(row=2, column=0)  # Position the label

        Entry(self.root, textvariable=self.max_battery).grid(row=0, column=1)
        Entry(self.root, textvariable=self.min_battery).grid(row=1, column=1)
        Entry(self.root, textvariable=self.alert_interval).grid(row=2, column=1)

        self.Chkbtn_Charging = Checkbutton(self.root, variable=self.disable_min_battery_alert_on_charging)
        self.Chkbtn_Charging.grid(row=3, column=0, columnspan=2, sticky='W')
        self.Chkbtn_nonCharging = Checkbutton(self.root, variable=self.disable_max_battery_alert_on_discharging)
        self.Chkbtn_nonCharging.grid(row=4, column=0, columnspan=2, sticky='W')

        self.start_button = Button(self.root, command=self.battery_checker.start_or_stop_check_battery_thread)
        self.start_button.grid(row=5, column=0, sticky="EW")

        self.minimize_button = Button(self.root, command=self.minimize_to_tray)
        self.minimize_button.grid(row=5, column=1, columnspan=2, sticky="EW")

        self.menu_options = (("Show", None, lambda systray: self.root.deiconify()),)
        self.systray = SysTrayIcon("icon.ico", "배터리 체커", self.menu_options, on_quit=self.on_quit_callback)

        # Create language change buttons
        for i, lang in enumerate(["en", "ko", "zh"]):
            Button(self.root, text=lang, command=lambda lang=lang: self.language_manager.change_language(lang)).grid(row=6, column=i, sticky="EW")
        
        Button(self.root, text="출력", command=lambda: print("check_battery_flag:", check_battery_flag.get(), self.battery_checker.check_battery_thread)).grid(row=7, column=0, sticky="EW")

        self.labels = {"Label_low_battery": self.Label_low_battery, "Label_max_battery": self.Label_max_battery, 
                       "Label_Alert_interval":self.Label_Alert_interval, "Chkbtn_Charging":self.Chkbtn_Charging, 
                       "Chkbtn_nonCharging":self.Chkbtn_nonCharging, "start_button":self.start_button, 
                       "minimize_button":self.minimize_button}

        update_texts(self.labels, self.current_language.get())
        self.root.mainloop()
    
    # Minimize to tray
    def minimize_to_tray(self):
        self.systray.start()
        self.root.withdraw()
    
    # Quit callback
    def on_quit_callback(self, systray):
        self.root.destroy()

if __name__ == "__main__":
    check_battery_flag = on_off_check(False)
    app = AppGUI()