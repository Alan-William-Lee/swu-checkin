import os
import sys
import argparse

from login import login
from get_token import get_token
from get_transition import get_transition_today
from checkin import checkin
from email_notifier import should_send_notification, get_notification_config


def main(
    username: str | None = None,
    password: str | None = None,
    email: str | None = None,
    student_id: str | None = None,
) -> int:
    """Run the check-in flow.

    Priority of credentials:
    1. Function args (if provided)
    2. Environment variables SWU_USERNAME and SWU_PASSWORD

    Email notification:
    - Set NOTIFICATION_EMAIL and NOTIFICATION_STUDENT_ID env vars to enable
    - Or pass via function args

    Returns exit code (0 success, non-zero on failure).
    """
    if not username or not password:
        # try environment
        env_user = os.environ.get("SWU_USERNAME")
        env_pass = os.environ.get("SWU_PASSWORD")
        if env_user and env_pass:
            username = username or env_user
            password = password or env_pass

    if not username or not password:
        print("缺少用户名或密码。请通过环境变量 SWU_USERNAME 和 SWU_PASSWORD 提供，或使用命令行参数。")
        return 2

    # 获取邮件通知配置（如果未通过参数传入）
    if not email or not student_id:
        env_email, env_student_id = get_notification_config()
        email = email or env_email
        student_id = student_id or env_student_id

    if not login(username, password):
        print("登录失败，账号或密码错误")
        return 3

    token = get_token(username, password)
    transition_today = get_transition_today(token)
    if not transition_today:
        print("暂无打卡任务")
        return 0
    if transition_today.get("qdzt") == "已签到":
        print("今日已打卡")
        return 0

    # 执行打卡，传入邮件通知参数
    checkin(token, email=email, student_id=student_id)
    print("打卡成功")

    # 如果配置了邮件通知，显示相关信息
    if email and student_id:
        print(f"已发送邮件通知至: {email}")
    else:
        print("未配置邮件通知（如需启用，请设置 NOTIFICATION_EMAIL 和 NOTIFICATION_STUDENT_ID 环境变量）")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SWU daily check-in runner")
    parser.add_argument("--username", "-u", help="SWU username (overrides SWU_USERNAME env)")
    parser.add_argument("--password", "-p", help="SWU password (overrides SWU_PASSWORD env)")
    parser.add_argument("--email", "-e", help="Notification email address (overrides NOTIFICATION_EMAIL env)")
    parser.add_argument("--student-id", "-s", help="Student ID for email notification (overrides NOTIFICATION_STUDENT_ID env)")
    args = parser.parse_args()

    exit_code = main(args.username, args.password, args.email, args.student_id)
    sys.exit(exit_code)
