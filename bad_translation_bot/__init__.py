import os
import random
import typing as t

import discord
from dotenv import load_dotenv
from google.cloud import translate_v2 as translate

__version__ = "0.1.0"
DEFAULT_FUCKERY = 16
MAX_FUCKERY = 32
MAX_CHARS = 1500
BOT_PREFIX = "$translate"
COMMAND_PREFIX = "-"
TRANSLATION_QUOTA = 480000
LOG_FILE = "chars_log.txt"
LANGUAGES = [
    "af",
    "am",
    "ar",
    "hy",
    "az",
    "eu",
    "be",
    "bn",
    "bs",
    "bg",
    "ca",
    "ceb",
    "zh",
    "zh-TW",
    "co",
    "hr",
    "cs",
    "da",
    "nl",
    "eo",
    "et",
    "fi",
    "fr",
    "fy",
    "gl",
    "ka",
    "de",
    "el",
    "gu",
    "ht",
    "ha",
    "haw",
    "he",
    "hi",
    "hmn",
    "hu",
    "is",
    "ig",
    "id",
    "ga",
    "it",
    "ja",
    "jv",
    "kn",
    "kk",
    "km",
    "rw",
    "ko",
    "ku",
    "ky",
    "lo",
    "lv",
    "lt",
    "lb",
    "mk",
    "mg",
    "ms",
    "ml",
    "mt",
    "mi",
    "mr",
    "mn",
    "my",
    "ne",
    "no",
    "ny",
    "or",
    "ps",
    "fa",
    "pl",
    "pt",
    "pa",
    "ro",
    "ru",
    "sm",
    "gd",
    "sr",
    "st",
    "sn",
    "sd",
    "si",
    "sk",
    "sl",
    "so",
    "es",
    "su",
    "sw",
    "sv",
    "tl",
    "tg",
    "ta",
    "tt",
    "te",
    "th",
    "tr",
    "tk",
    "uk",
    "ur",
    "ug",
    "uz",
    "vi",
    "cy",
    "xh",
    "yi",
    "yo",
    "zu",
]

load_dotenv()
discord_token = os.environ.get("DISCORD_TOKEN")

discord_client = discord.Client()
translate_client = translate.Client()


@discord_client.event
async def on_ready():
    print(f"Logged in as {discord_client.user}")


@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    if message.content.startswith(BOT_PREFIX):
        content: t.List[str] = message.content.split(" ", 1)
        if len(content) == 1 and content[0] == "$translate":
            await help_text(message.channel)
            return
        text = content[1]
        fuckery = DEFAULT_FUCKERY
        if text.startswith(COMMAND_PREFIX):
            command = text[1:]
            if command == "help":
                await help_text(message.channel)
                return
            if command.startswith("fuckery"):
                subcommand = command.split(" ", 2)
                if len(subcommand) <= 2:
                    print("No subcommand provided")
                    await invalid_fuckery(message.channel)
                    return
                try:
                    fuckery = int(subcommand[1])
                    if not 0 <= fuckery <= MAX_FUCKERY:
                        raise ValueError("Fuckery not in valid range")
                except ValueError:
                    await invalid_fuckery(message.channel)
                    return
                text = subcommand[2]
            else:
                await help_text(message.channel, messed_up=True)
                return
        if len(text) > MAX_CHARS:
            await text_too_long(message.channel, len(text))
            return
        if read_translation_chars() + len(text) * (fuckery + 1) >= TRANSLATION_QUOTA:
            await rate_limit(message.channel)
            return
        input_language = "en"
        for i in range(1, fuckery + 1):
            if i % 6 == 0 and i <= fuckery:
                print(f"Translating from {output_language} to en")
                text = await translate_text(
                    message.channel, text, output_language, "en"
                )
                input_language = "en"
            while True:
                output_language = LANGUAGES[random.randint(0, len(LANGUAGES) - 1)]
                if output_language != input_language:
                    break
            print(f"Translating from {input_language} to {output_language}")
            text = await translate_text(
                message.channel, text, input_language, output_language
            )
            input_language = output_language
        print(f"Translating from {input_language} to en")
        text = await translate_text(message.channel, text, input_language, "en")
        await message.channel.send(text)


async def help_text(channel, messed_up: bool = False) -> None:
    text = ""
    if messed_up:
        text += (
            "Uwu you made a fucky wucky!! A wittle fucko boingo!"
            " Dat's not how I work!\n"
        )
    text += f'Type "{BOT_PREFIX} [TEXT]" to badly translate text.\n'
    text += "To set the amount of translation fuckery, type "
    text += f'"{BOT_PREFIX} {COMMAND_PREFIX}fuckery # [TEXT]", '
    text += f"where # is the amount of fuckery you desire (Max value: {MAX_FUCKERY}). "
    text += f"The default amount of fuckery is {DEFAULT_FUCKERY}."
    await channel.send(text)


async def invalid_fuckery(channel) -> None:
    text = (
        "Uwu you made a fucky wucky!! A wittle fucko boingo!"
        " Fuckery isn't used like dat :-(\n"
    )
    text += (
        f'Type "{BOT_PREFIX} {COMMAND_PREFIX}fuckery # [TEXT]", where # is the amount '
    )
    text += f"of fuckery you desire (Max value: {MAX_FUCKERY}). "
    text += f"The default amount of fuckery is {DEFAULT_FUCKERY}"
    await channel.send(text)


async def text_too_long(channel, text_length: int) -> None:
    text = (
        "Uwu you made a fucky wucky!! A wittle fucko boingo!"
        " I couldn't twanswate yow text :-(\n"
    )
    text += f"Character limit exceeded: {text_length}/{MAX_CHARS}"
    await channel.send(text)


async def rate_limit(channel) -> None:
    text = (
        "Uwu you made a fucky wucky!! A wittle fucko boingo!"
        " I couldn't twanswate yow text :-(\n"
    )
    text += "You used me too much! I don't wanna cost my creator money."
    await channel.send(text)


def create_chars_log() -> None:
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as chars_log:
            chars_log.write("0")


def add_translation_chars(num_chars: int) -> None:
    with open(LOG_FILE, "r+") as chars_log:
        num_translation_chars = int(chars_log.read()) + num_chars
        chars_log.seek(0)
        chars_log.write(str(num_translation_chars))
        chars_log.truncate()


def read_translation_chars() -> int:
    with open(LOG_FILE, "r") as chars_log:
        num_translation_chars = int(chars_log.read())
    return num_translation_chars


async def translate_text(channel, text: str, input_language: str, output_language: str):
    translation_result: dict = translate_client.translate(
        text,
        format_="text",
        source_language=input_language,
        target_language=output_language,
    )
    translation = translation_result.get("translatedText")
    if not translation:
        text = (
            "Uwu I made a fucky wucky!! A wittle fucko boingo!"
            " I couldn't twanswate yow text :-("
        )
        await channel.send(text)
        raise RuntimeError("Couldn't translate text")
    add_translation_chars(len(text))
    return translation


if __name__ == "__main__":
    create_chars_log()
    discord_client.run(discord_token)
