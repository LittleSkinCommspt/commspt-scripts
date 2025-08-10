import datetime
import zoneinfo

import httpx
from loguru import logger

from utils.config_manager import config
from utils.httpx_requests import littleskin_api_base
from utils.send_message import group_message

PERIOD = 1


def get_past_morning(days: int = 1) -> str:
    """
    获取中国标准时间指定天数前的 05:00 日期时间对象，并格式化为 'YYYY-MM-DD HH:MM' 字符串。

    Args:
        days (int): 要追溯的天数，默认为 1 (昨天)。

    Returns:
        str: 格式化后的日期时间字符串，格式为 'YYYY-MM-DD HH:MM'。
    """
    past_date = datetime.date.today() - datetime.timedelta(days=days)
    past_morning = datetime.datetime.combine(past_date, datetime.time.min) + datetime.timedelta(hours=5)
    past_morning_cn = past_morning.replace(tzinfo=zoneinfo.ZoneInfo("Asia/Shanghai"))
    return past_morning_cn.strftime("%Y-%m-%d %H:%M")


def get_registration_statistics(period: int = PERIOD):
    """
    获取注册统计信息，并发送消息到指定群组。
    """

    start_time = get_past_morning(days=period)
    end_time = get_past_morning(days=0)

    logger.debug(f"from {start_time} to {end_time}")
    logger.info("Fetching data...")

    with httpx.Client(**littleskin_api_base) as client:
        # 获取期间内全部注册用户数量
        response = client.get(
            "/admin/users", params={"q": f"register_at >= '{start_time}' and register_at <= '{end_time}'"}
        )
        response_body = response.json()
        common_users = response_body.get("total")

        logger.success(f"🆕 Found {common_users} users registered")

        # 获取期间内已验证邮箱的用户数量
        response = client.get(
            "/admin/users", params={"q": f"register_at >= '{start_time}' and register_at <= '{end_time}' and verified"}
        )
        response_body = response.json()
        verified_users = response_body.get("total")

        logger.success(f"📧 Found {verified_users} users registered with verified emails")

    # 计算百分比
    percentage = round(verified_users / common_users * 100, 2)
    logger.info(f"📊 {percentage}% of users registered with verified emails")

    # 发送消息
    logger.info("Sending message...")
    group_message(
        config.groups_ids.commspt,
        f"""📊 新增用户统计（近{period}天）

自 {start_time}
至 {end_time}

» 新增用户数：{common_users}
» 邮箱验证率：{percentage}%""",
    )


if __name__ == "__main__":
    get_registration_statistics()
