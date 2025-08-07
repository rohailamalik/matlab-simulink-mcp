from pydantic_settings import BaseSettings, SettingsConfigDict
from utils.utils import get_path
from pathlib import Path


class Settings(BaseSettings):
    mode: str = "DEV"
    logs_path: Path = "logs"
    matlab_helpers_path: Path = "data/helpers"
    security_wrappers_path: Path = "data/security/wrappers"
    simlib_database_path: Path = "data/simlib_db.json"
    blacklist_commands_path: Path = "data/blacklist.txt"
    sandbox: bool = False

    openai_api_key: str = None
    tavily_api_key: str = None

    model_config = SettingsConfigDict(env_file=get_path(".env"))

settings = Settings()