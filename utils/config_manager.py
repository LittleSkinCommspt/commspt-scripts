from typing import Annotated
import yaml
from pydantic import BaseModel
from pathlib import Path


class OneBotAPIConfig(BaseModel):
    endpoint: str
    access_token: str

    @property
    def auth_header(self):
        return {"Authorization": f"Bearer {self.access_token}"}


class LittleSkinConfig(BaseModel):
    endpoint: str
    access_token: str

    @property
    def auth_header(self):
        return {"Authorization": f"Bearer {self.access_token}"}


class GroupsIdsConfig(BaseModel):
    commspt: int

class AzureAPIConfig(BaseModel):
    client_id: str
    client_secret: str
    login_id: str
    log_workspace_id: str

class OracleCloudConfig(BaseModel):
    user: str
    key_file: Annotated[Path, str] = Path.cwd() / "oci_api_key.pem"
    fingerprint: str
    tenancy: str
    region: str
    compartment_id: str
    log_group_id: str
    log_object_id_accepted: str
    log_object_id_relayed: str

class Config(BaseModel):
    onebot_api: OneBotAPIConfig
    littleskin: LittleSkinConfig
    groups_ids: GroupsIdsConfig
    azure_api: AzureAPIConfig
    oracle_cloud: OracleCloudConfig


_loaded_config = yaml.safe_load(open(".config.yaml", "r", encoding="utf-8"))

config = Config(**_loaded_config)
