from pydantic_settings import BaseSettings, SettingsConfigDict
from utils.utils import get_path
from pathlib import Path


class Settings(BaseSettings):
    mode: str 
    logs_path: Path
    matlab_helpers_path: Path
    security_wrappers_path: Path
    sl_lib_data_path: Path
    openai_api_key: str = None
    tavily_api_key: str = None
    advanced_security: bool = False

    model_config = SettingsConfigDict(env_file=get_path(".env"))

settings = Settings()