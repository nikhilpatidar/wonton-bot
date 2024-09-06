from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    # Telegram API settings
    API_ID: int = 0
    API_HASH: str = ''

    # Referral settings
    REF_ID: str = 'K3AWKBV9'

    # Farming settings
    AUTO_FARMING: bool = True

    # Daily reward settings
    AUTO_DAILY_REWARD: bool = True

    # Game settings
    AUTO_PLAY_GAME: bool = True
    POINTS_COUNT: List[int] = [100, 300]

    # Task settings
    AUTO_TASK: bool = True

    # User agent settings
    FAKE_USERAGENT: bool = False
    AUTO_CLAIM_INVITE_REWARDS: bool = True
    # Delay settings
    USE_RANDOM_DELAY_IN_RUN: bool = False
    RANDOM_DELAY_IN_RUN: List[int] = [0, 15]

    # Proxy settings
    USE_PROXY_FROM_FILE: bool = False

settings = Settings()