import requests

def get_transition_today(token):
    url = "https://of.swu.edu.cn//gateway/fighter-baida/api/cqtj/getTransitionByToday"
    headers = {"fighter-auth-token": token}
    data = {"pageNum": 1,"pageSize": 1,}
    response = requests.post(url, headers=headers, data=data).json()["data"]["records"]
    return response[0] if response else None
