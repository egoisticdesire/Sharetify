import logging
import subprocess
import sys

from telethon import errors as telethon_errors
from telethon.sync import TelegramClient

from config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.system.debug else logging.WARNING,
    format=settings.system.logging_format,
    datefmt=settings.system.logging_date_format,
)


def get_spotify_track() -> tuple[str | None, str | None]:
    """
    Gets information about the current track in Spotify.

    Returns:
        Tuple of track URL and title.
        If the track is not found, or an error occurs, returns (None, None).
    """
    apple_script = """
    tell application "Spotify"
        try
            if player state is playing then
                set trackID to id of current track
                set trackName to name of current track
                set artistName to artist of current track
                if trackID starts with "spotify:track:" then
                    return trackID & "###" & artistName & " － " & trackName
                end if
            end if
        on error errMsg
            return ""
        end try
    end tell
    """

    try:
        result = (
            subprocess.check_output(["osascript", "-e", apple_script])
            .decode("utf-8")
            .strip()
        )

        if not result:
            logging.warning("Spotify is not playing any track.")
            return None, None

        track_id, track_title = result.split("###")
        track_url = f'{settings.spotify.url}{track_id.split(":")[-1]}'
        logging.info("Current track: %s (%s)", track_title, track_url)
        return track_url, track_title

    except subprocess.CalledProcessError as e:
        logging.error("Error executing AppleScript: %s", e)
        return None, None


def send_track() -> None:
    """
    Sends information about the current track to Telegram.
    """
    try:
        track_url, track_title = get_spotify_track()
        if not track_url:
            logging.error("No track to send.")
            return

        with TelegramClient(
            settings.telegram.session,
            settings.telegram.api_id,
            settings.telegram.api_hash,
        ) as client:
            message = (
                settings.spotify.ru_message
                if "ru" in settings.system.language.lower()
                else settings.spotify.en_message
            )
            message += settings.spotify.track_prefix.format(
                url=track_url,
                title=track_title,
            )

            client.send_message(
                entity=settings.telegram.target_user,
                message=message,
                parse_mode=settings.telegram.parse_mode,
                link_preview=settings.telegram.link_preview,
            )
            logging.info("Track sent successfully!")

    except (ConnectionError, ValueError, OSError, telethon_errors.RPCError) as e:
        error_message = f"Configuration error: {str(e).split(" - ")[-1].strip()}"
        sys.exit(error_message)


if __name__ == "__main__":
    send_track()
