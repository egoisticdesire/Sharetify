import sys
import webbrowser

from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class SystemSettings(BaseModel):
    debug: bool = False
    language: str = "en"
    logging_format: str = "%(asctime)s - %(name)s - %(levelname)-7s - %(message)s"
    logging_date_format: str = "%Y-%m-%d %H:%M:%S"


class SpotifySettings(BaseModel):
    url: str = "https://open.spotify.com/track/"
    ru_message: str = "🎵 В <b>Spotify</b> сейчас играет:\n"
    en_message: str = "🎵 <b>Spotify</b> is playing now:\n"
    track_prefix: str = '🔥 <b><a href="{url}">{title}</a></b>'


class TelegramSettings(BaseModel):
    api_id: int
    api_hash: str
    target_user_id: int
    session: str = "session"
    parse_mode: str = "html"
    link_preview: bool = False


class Settings(BaseSettings):
    system: SystemSettings = SystemSettings()
    spotify: SpotifySettings = SpotifySettings()
    telegram: TelegramSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP__",
        env_nested_delimiter="__",
        case_sensitive=False,
    )


try:
    settings = Settings()  # noqa
except ValidationError as e:
    print(
        "Ошибка конфигурации: отсутствуют необходимые переменные окружения.",
        "Configuration Error: there are no necessary variables of the environment.",
        e,
        sep="\n",
    )
    if "target_user_id" in str(e):
        webbrowser.open("https://t.me/getmyid_bot")
    else:
        webbrowser.open("https://my.telegram.org")
    sys.exit(1)
