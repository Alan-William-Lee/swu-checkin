import requests
import os
import urllib.parse


def send_checkin_notification(email: str, student_id: str, use_backup: bool = False) -> bool:
    """
    发送打卡成功邮件通知
    
    Args:
        email: 接收通知的邮箱地址
        student_id: 学生学号
        use_backup: 是否使用备用API（简化版）
    
    Returns:
        bool: 发送是否成功
    """
    # 主API（完整参数）
    primary_api = (
        f"https://ygwyy.top/邮箱/index.php"
        f"?email={urllib.parse.quote(email)}"
        f"&username={urllib.parse.quote(student_id)}"
        f"&emailSubject={urllib.parse.quote('钉钉查寝打卡')}"
        f"&verificationPurpose={urllib.parse.quote('自动打卡')}"
        f"&welcomeMsg={urllib.parse.quote('您今日的钉钉查寝打卡已完成')}"
        f"&welcomeMsgEn={urllib.parse.quote('Your automatic check-in for today has been completed')}"
        f"&siteNameCn={urllib.parse.quote('钉钉查寝打卡')}"
    )
    
    # 备用API（简化版）
    backup_api = (
        f"https://ygwyy.top/邮箱/index.php"
        f"?email={urllib.parse.quote(email)}"
        f"&username={urllib.parse.quote(student_id)}"
    )
    
    api_url = backup_api if use_backup else primary_api
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        # 检查响应内容判断是否成功
        # 根据API实际返回格式调整判断逻辑
        if response.status_code == 200:
            print(f"邮件通知发送成功: {email}")
            return True
        else:
            print(f"邮件通知发送失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("邮件通知请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"邮件通知请求异常: {e}")
        return False


def send_notification_with_fallback(email: str, student_id: str) -> bool:
    """
    发送通知，主API失败时自动尝试备用API
    
    Args:
        email: 接收通知的邮箱地址
        student_id: 学生学号
    
    Returns:
        bool: 最终发送是否成功
    """
    # 先尝试主API
    if send_checkin_notification(email, student_id, use_backup=False):
        return True
    
    print("主API发送失败，尝试备用API...")
    
    # 主API失败，尝试备用API
    if send_checkin_notification(email, student_id, use_backup=True):
        return True
    
    print("备用API也发送失败")
    return False


def get_notification_config() -> tuple[str | None, str | None]:
    """
    从环境变量获取邮件通知配置
    
    Returns:
        tuple: (email, student_id) 如果未配置则返回 (None, None)
    """
    email = os.environ.get("NOTIFICATION_EMAIL")
    student_id = os.environ.get("NOTIFICATION_STUDENT_ID")
    return email, student_id


def should_send_notification() -> bool:
    """
    检查是否配置了邮件通知
    
    Returns:
        bool: 是否配置了通知
    """
    email, student_id = get_notification_config()
    return email is not None and student_id is not None
