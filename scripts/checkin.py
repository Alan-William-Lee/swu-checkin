import requests
import time
import json
from get_transition import get_transition_today
from get_info import get_student_id
from email_notifier import send_notification_with_fallback


def checkin(token, email: str | None = None, username: str | None = None):
    transition = get_transition_today(token)
    if transition is None:
        return None
    formid = transition["formId"]
    id = transition["id"]
    url = "https://of.swu.edu.cn/gateway/fighter-baida/api/form-instance/save"
    params = {"formId": formid, "isSubmitProcess": False}
    headers = {"fighter-auth-token": token, "Content-Type": "application/json;charset=UTF-8"}
    payload = {
        "id": id,
        "formId": formid,
        "tsrq": time.strftime("%Y-%m-%d"),
        "xh": get_student_id(token),
        "qdsj": ["21:00", "23:30"],
    }
    response = requests.post(url, headers=headers, params=params, data=json.dumps(payload)).json()["data"]
    
    # 打卡成功后发送邮件通知
    if response is not None and email and username:
        try:
            send_notification_with_fallback(email, username)
        except Exception as e:
            # 邮件发送失败不影响打卡结果
            print(f"邮件通知发送失败（不影响打卡）: {e}")
    
    return response

