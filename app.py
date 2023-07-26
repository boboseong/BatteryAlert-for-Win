import ctypes
import time
import threading
import psutil
from functools import partial
from tkinter import Tk, Label, Entry, Button, Checkbutton, StringVar, IntVar, Toplevel
from infi.systray import SysTrayIcon

MB_ICONWARNING = 0x30
MB_SYSTEMMODAL = 0x1000
check_battery_thread = None
check_battery_flag = True

# 언어별 텍스트 딕셔너리
TEXTS = {
    "en": {
        "max_battery": "Max Battery (%)",
        "min_battery": "Min Battery (%)",
        "alert_interval": "Alert Interval (min)",
        "disable_min_battery": "Disable min battery alert when charging",
        "disable_max_battery": "Disable max battery alert when not charging",
        "start": "Start",
        "stop": "Stop",
        "minimize": "Minimize to Tray",
        "warning": "Warning",
        "battery_status": "Battery status is out of range. Current battery: {}%",
    },
    "ko": {
        "max_battery": "최대 배터리 (%)",
        "min_battery": "최소 배터리 (%)",
        "alert_interval": "알림 주기 (분)",
        "disable_min_battery": "충전 중일 때 최소 배터리 경고 끄기",
        "disable_max_battery": "충전 중이 아닐 때 최대 배터리 경고 끄기",
        "start": "시작",
        "stop": "중지",
        "minimize": "트레이로 최소화",
        "warning": "경고",
        "battery_status": "배터리 상태가 설정된 범위를 벗어났습니다. 현재 배터리: {}%",
    },
    "zh": {
        "max_battery": "最大电池 (%)",
        "min_battery": "最小电池 (%)",
        "alert_interval": "警报间隔 (分钟)",
        "disable_min_battery": "充电时关闭最小电池警告",
        "disable_max_battery": "未充电时关闭最大电池警告",
        "start": "开始",
        "stop": "停止",
        "minimize": "最小化到托盘",
        "warning": "警告",
        "battery_status": "电池状态超出范围。当前电池： {}%",
    },
}

# 윈도우 알림 함수
def message_box(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 1)

# 배터리 상태 확인 함수
def check_battery(check_battery_flag):
    while check_battery_flag:
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
                
        for _ in range(int(alert_interval.get()) * 60):  # 알림 주기 동안 1초 간격으로 체크
            if not check_battery_flag:  # 종료 플래그가 설정되면 함수를 종료
                return
            time.sleep(1)

# 배터리 체크 스레드 실행 함수
def start_or_stop_check_battery_thread(check_battery_thread, check_battery_flag):

    if check_battery_thread is not None and check_battery_thread.is_alive():  # 스레드가 이미 실행 중이면 종료
        check_battery_flag = False
        check_battery_thread.join()  # 스레드가 종료될 때까지 기다림
        start_button.config(text=TEXTS[current_language.get()]["start"])  # 버튼 텍스트를 '시작'으로 변경
    else:  # 스레드가 실행 중이지 않으면 시작
        write_settings()
        check_battery_flag = True  # 새로운 스레드를 위한 실행 플래그를 설정
        check_battery_thread = threading.Thread(target=check_battery, args=(check_battery_flag,))
        check_battery_thread.start()
        start_button.config(text=TEXTS[current_language.get()]["stop"])  # 버튼 텍스트를 '작동 중'으로 변경

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
def change_language(new_language):
    current_language.set(new_language)
    write_settings()
    update_texts()

# 버튼 텍스트 업데이트 함수
def update_texts():
    start_button.config(text=TEXTS[current_language.get()]["start"])
    minimize_button.config(text=TEXTS[current_language.get()]["minimize"])
    Label_max_battery.config(text=TEXTS[current_language.get()]["max_battery"])
    Label_low_battery.config(text=TEXTS[current_language.get()]["min_battery"])
    Label_Alert_interval.config(text=TEXTS[current_language.get()]["alert_interval"])
    Chkbtn_Charging.config(text=TEXTS[current_language.get()]["disable_min_battery"])
    Chkbtn_nonCharging.config(text=TEXTS[current_language.get()]["disable_max_battery"])
    # 나머지 위젯 텍스트를 여기에 업데이트

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

Chkbtn_Charging = Checkbutton(root, text="충전 중일 때 최소 배터리 경고 끄기", variable=disable_min_battery_alert_on_charging)
Chkbtn_Charging.grid(row=3, column=0, columnspan=2, sticky='W')
Chkbtn_nonCharging = Checkbutton(root, text="충전 중이 아닐 때 최대 배터리 경고 끄기", variable=disable_max_battery_alert_on_discharging)
Chkbtn_nonCharging.grid(row=4, column=0, columnspan=2, sticky='W')

start_button = Button(root, text="시작", command=partial(start_or_stop_check_battery_thread, check_battery_thread, check_battery_flag))
start_button.grid(row=5, column=0, sticky="EW")

minimize_button = Button(root, text="트레이로 최소화", command=minimize_to_tray)
minimize_button.grid(row=5, column=1, columnspan=2, sticky="EW")

menu_options = (("Show", None, lambda systray: root.deiconify()),)
systray = SysTrayIcon("icon.ico", "배터리 체커", menu_options, on_quit=on_quit_callback)

Button(root, text="English", command=lambda: change_language("en")).grid(row=6, column=0, sticky="EW")
Button(root, text="한국어", command=lambda: change_language("ko")).grid(row=6, column=1, sticky="EW")
Button(root, text="中文", command=lambda: change_language("zh")).grid(row=6, column=2, sticky="EW")

read_settings()  # 프로그램 시작 시 저장된 설정 읽기
update_texts()
root.mainloop()