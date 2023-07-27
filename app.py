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
check_battery_thread = None

class on_off_check:
    def __init__(self, on_off):
        self.on_off = on_off

    def get(self):
        return self.on_off
    
    def turn_on(self):
        self.on_off = True

    def turn_off(self):
        self.on_off = False
check_battery_flag = on_off_check(False)

# 윈도우 알림 함수
def message_box(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 1)

# 배터리 상태 확인 함수
def check_battery(check_battery_flag):
    while check_battery_flag.get():
        battery = psutil.sensors_battery()
        percent = battery.percent
        charging = battery.power_plugged

        if ((not charging and percent < float(min_battery.get())) or
           (charging and not disable_min_battery_alert_on_charging.get() and percent < float(min_battery.get())) or
           (charging and percent > float(max_battery.get())) or
           (not charging and not disable_max_battery_alert_on_discharging.get() and percent > float(max_battery.get()))):
            root.deiconify()
            ctypes.windll.user32.MessageBoxW(0, 
                TEXTS[current_language.get()]["battery_status"].format(percent), 
                TEXTS[current_language.get()]["warning"], 
                MB_ICONWARNING | MB_SYSTEMMODAL)
                
        for _ in range(int(alert_interval.get()) * 300):  # 알림 주기 동안 0.2초 간격으로 체크
            if not check_battery_flag.get():  # 종료 플래그가 설정되면 함수를 종료
                return
            time.sleep(0.2)

# 배터리 체크 스레드 실행 함수
def start_or_stop_check_battery_thread(check_battery_flag):
    global check_battery_thread
    if check_battery_thread is not None and check_battery_thread.is_alive():  # 스레드가 이미 실행 중이면 종료
        check_battery_flag.turn_off()  # 종료 플래그를 설정
        check_battery_thread.join()  # 스레드가 종료될 때까지 기다림
        start_button.config(text=TEXTS[current_language.get()]["start"])  # 버튼 텍스트를 '시작'으로 변경
    else:  # 스레드가 실행 중이지 않으면 시작
        write_settings()
        check_battery_flag.turn_on() # 새로운 스레드를 위한 실행 플래그를 설정
        check_battery_thread = threading.Thread(target=check_battery, args=(check_battery_flag,))
        check_battery_thread.start()
        start_button.config(text=TEXTS[current_language.get()]["stop"])  # 버튼 텍스트를 '중지'로 변경

# 설정 파일 읽기 함수
def read_settings():
    try:
        with open("settings.txt", "r") as file:
            max_battery.set(file.readline().strip())
            min_battery.set(file.readline().strip())
            alert_interval.set(file.readline().strip())
            disable_min_battery_alert_on_charging.set(int(file.readline().strip()))
            disable_max_battery_alert_on_discharging.set(int(file.readline().strip()))
            current_language.set(file.readline().strip())
    except FileNotFoundError:
        current_language.set("en")  # 파일이 없으면 기본 언어를 영어로 설정
        pass  # 파일이 없으면 아무것도 하지 않음

# 설정 파일 쓰기 함수
def write_settings():
    with open("settings.txt", "w") as file:
        file.write(max_battery.get() + "\n")
        file.write(min_battery.get() + "\n")
        file.write(alert_interval.get() + "\n")
        file.write(str(disable_min_battery_alert_on_charging.get()) + "\n")
        file.write(str(disable_max_battery_alert_on_discharging.get()) + "\n")
        file.write(current_language.get() + "\n")

#시스템 트레이로 보내기
def on_quit_callback(systray):
    root.destroy()

def minimize_to_tray():
    systray.start()
    root.withdraw()

# 언어 변경 함수
def change_language(new_language, check_battery_flag):
    current_language.set(new_language)
    write_settings()
    update_texts(labels, current_language.get())
    if check_battery_flag.get():
        start_or_stop_check_battery_thread(check_battery_flag)
        start_or_stop_check_battery_thread(check_battery_flag)

# Tkinter GUI
root = Tk()
root.title("My Application")
root.resizable(0, 0)  # disable window resizing

# 현재 언어 변수
current_language = StringVar()

# Create the label
Label_max_battery = Label(root)
Label_low_battery = Label(root)
Label_Alert_interval = Label(root)

Label_max_battery.grid(row=0, column=0)  # Position the label
Label_low_battery.grid(row=1, column=0)  # Position the label
Label_Alert_interval.grid(row=2, column=0)  # Position the label

max_battery = StringVar()
min_battery = StringVar()
alert_interval = StringVar()
disable_min_battery_alert_on_charging = IntVar()
disable_max_battery_alert_on_discharging = IntVar()

Entry(root, textvariable=max_battery).grid(row=0, column=1)
Entry(root, textvariable=min_battery).grid(row=1, column=1)
Entry(root, textvariable=alert_interval).grid(row=2, column=1)

Chkbtn_Charging = Checkbutton(root, variable=disable_min_battery_alert_on_charging)
Chkbtn_Charging.grid(row=3, column=0, columnspan=2, sticky='W')
Chkbtn_nonCharging = Checkbutton(root, variable=disable_max_battery_alert_on_discharging)
Chkbtn_nonCharging.grid(row=4, column=0, columnspan=2, sticky='W')

start_button = Button(root, command=partial(start_or_stop_check_battery_thread, check_battery_flag))
start_button.grid(row=5, column=0, sticky="EW")

minimize_button = Button(root, command=minimize_to_tray)
minimize_button.grid(row=5, column=1, columnspan=2, sticky="EW")

menu_options = (("Show", None, lambda systray: root.deiconify()),)
systray = SysTrayIcon("icon.ico", "배터리 체커", menu_options, on_quit=on_quit_callback)

Button(root, text="English", command=lambda: change_language("en", check_battery_flag)).grid(row=6, column=0, sticky="EW")
Button(root, text="한국어", command=lambda: change_language("ko", check_battery_flag)).grid(row=6, column=1, sticky="EW")
Button(root, text="中文", command=lambda: change_language("zh", check_battery_flag)).grid(row=6, column=2, sticky="EW")
Button(root, text="출력", command=lambda: print("check_battery_flag:", check_battery_flag.get(), check_battery_thread)).grid(row=7, column=0, sticky="EW")

labels = {"Label_low_battery": Label_low_battery, "Label_max_battery": Label_max_battery, "Label_Alert_interval":Label_Alert_interval, "Chkbtn_Charging":Chkbtn_Charging, "Chkbtn_nonCharging":Chkbtn_nonCharging, "start_button":start_button, "minimize_button":minimize_button}
read_settings()  # 프로그램 시작 시 저장된 설정 읽기
update_texts(labels, current_language.get())
root.mainloop()