from pydantic_settings import BaseSettings, SettingsConfigDict
from utils.utils import get_path

class Settings(BaseSettings):
    mode: str
    logs_path: str
    matlab_helpers_path: str
    sl_lib_data_path: str

    model_config = SettingsConfigDict(env_file=get_path(".env"), extra="ignore")

settings = Settings()