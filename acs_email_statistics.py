import httpx
from loguru import logger

from utils.config_manager import config
from utils.send_message import group_message
from utils.httpx_requests import any_api_base

KQL = """
ACSEmailStatusUpdateOperational
| where isnotempty(RecipientId)
| summarize TotalCount = dcount(CorrelationId),
            TotalRecipient = dcount(RecipientId),
            Undelivered = count(DeliveryStatus != "Delivered"),
            HardBounced = count(IsHardBounce == True)
"""

TIMESPAN = "P1D"

def get_access_token():
    logger.debug("Getting Azure access token")
    with httpx.Client(base_url="https://login.microsoftonline.com/", **any_api_base) as client:
        response = client.post(
            f"/{config.azure_api.login_id}/oauth2/v2.0/token",
            data={
                "grant_type": "client_credentials",
                "client_id": config.azure_api.client_id,
                "client_secret": config.azure_api.client_secret,
                "scope": "https://api.loganalytics.io/.default",
            },
        )
    access_token = response.json()["access_token"]
    logger.success("Got Azure access token")
    return access_token


def process_data(data: dict):
    rows = data["tables"][0]["rows"][0]
    columns = [col["name"] for col in data["tables"][0]["columns"]]
    result: dict[str, int | str] = {columns[i]: rows[i] for i in range(len(columns))}
    return result
    

def get_acs_email_statistics():
    logger.debug("Querying Azure Log Analytics by KQL...")

    with httpx.Client(base_url="https://api.loganalytics.azure.com/", **any_api_base) as client:
        response = client.post(
            f"/v1/workspaces/{config.azure_api.log_workspace_id}/query",
            headers={"Authorization": f"Bearer {get_access_token()}"},
            json={"query": KQL, "timespan": TIMESPAN},
        )

    result = process_data(response.json())
    logger.success(result)

    statistics = [f"{k}: {v}" for k, v in result.items()]
    
    message = f"""📊 ACS Email 统计 [{TIMESPAN}]
    
{"\n".join(statistics)}"""
    group_message(config.groups_ids.commspt, message)


if __name__ == "__main__":
    get_acs_email_statistics()
