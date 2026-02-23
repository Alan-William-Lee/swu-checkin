import requests
import time
import json
from get_transition import get_transition_today
from get_info import get_student_id
def checkin(token):
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
    return response

