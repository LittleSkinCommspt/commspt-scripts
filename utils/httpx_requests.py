from utils.config_manager import config

littleskin_api_base = {
    "headers": config.littleskin.auth_header,
    "base_url": config.littleskin.endpoint,
    "follow_redirects": True,
    "http2": True,
}
