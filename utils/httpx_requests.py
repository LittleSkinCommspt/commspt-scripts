from typing import Any
from utils.config_manager import config

any_api_base: dict[str, Any] = {
    "follow_redirects": True,
    "http2": True,
}

littleskin_api_base = any_api_base | {
    "headers": config.littleskin.auth_header,
    "base_url": config.littleskin.endpoint,
}
