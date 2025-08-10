import httpx
from loguru import logger

from .config_manager import config


def group_message(group_id: int, message: str):
    """
    发送消息到指定群组

    Args:
        group_id (int): 群号
        message (str): 消息
    """
    logger.info(f"Sending message to group {group_id}")
    with httpx.Client(
        headers=config.onebot_api.auth_header,
        base_url=config.onebot_api.endpoint,
        http2=True,
        follow_redirects=True,
    ) as client:
        response = client.post(
            "/send_group_msg",
            json={
                "group_id": group_id,
                "message": message,
            },
        )

    logger.debug(response.text)
