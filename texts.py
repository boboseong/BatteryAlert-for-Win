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

# 버튼 텍스트 업데이트 함수
def update_texts(labels, current_language):
    labels["start_button"].config(text=TEXTS[current_language]["start"])
    labels["minimize_button"].config(text=TEXTS[current_language]["minimize"])
    labels["Label_max_battery"].config(text=TEXTS[current_language]["max_battery"])
    labels["Label_low_battery"].config(text=TEXTS[current_language]["min_battery"])
    labels["Label_Alert_interval"].config(text=TEXTS[current_language]["alert_interval"])
    labels["Chkbtn_Charging"].config(text=TEXTS[current_language]["disable_min_battery"])
    labels["Chkbtn_nonCharging"].config(text=TEXTS[current_language]["disable_max_battery"])
    # 나머지 위젯 텍스트를 여기에 업데이트