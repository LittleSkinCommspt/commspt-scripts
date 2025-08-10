import yaml
from pydantic import BaseModel


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


class Config(BaseModel):
    onebot_api: OneBotAPIConfig
    littleskin: LittleSkinConfig
    groups_ids: GroupsIdsConfig


_loaded_config = yaml.safe_load(open(".config.yaml", "r", encoding="utf-8"))

config = Config(**_loaded_config)
