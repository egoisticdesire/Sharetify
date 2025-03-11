import sys
import webbrowser

from pydantic import BaseModel, field_validator, ValidationError
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
    target_user: int | str
    session: str = "session"
    parse_mode: str = "html"
    link_preview: bool = False

    @field_validator("target_user", mode="before")
    def validate_target_user(cls, v):
        if v and v.startswith("@"):
            return v
        return int(v)


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
    # print(e)
    if "target_user" in str(e):
        message = "You need to specify the user ID or username in the environment"
    else:
        message = "You need to specify the API ID and API Hash in the environment"
        webbrowser.open("https://my.telegram.org")
    sys.exit(f"Configuration error: {message}")
