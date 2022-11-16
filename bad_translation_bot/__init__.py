import datetime
import json
import os
import random
import re
import typing as t
from pathlib import Path

import discord
import emoji
import validators
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
COOLDOWN = 5
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
intents = discord.Intents.default()
intents.messages = True  # pylint: disable=assigning-non-slot
intents.message_content = True  # pylint: disable=assigning-non-slot
discord_client = discord.Client(intents=intents)
translate_client = translate.Client()

emoji_regex = re.compile(r"<a?:\w*:\d*>")
spaces_regex = re.compile(r"\s+")
mention_regex = re.compile(r"(<@&?\d+>|@everyone|@here)")
cape_regex = re.compile(r"\bcape\b", flags=re.IGNORECASE)
solve_south_context = re.compile(r"\b(solve|south)\b", flags=re.IGNORECASE)
shitter_context = re.compile(r"\bshitter[s]?\b", re.IGNORECASE)
cheese_context = re.compile(r"\bcheese\b")

LAST_TIMESTAMPS: dict[int, datetime.datetime] = {}
MEMES_AND_COPYPASTAS: dict = {}


def load_copypastas():
    with open("copypastas.json", "r", encoding="UTF-8") as copypastas_file:
        copypastas = json.load(copypastas_file)["copypastas"]
    meme_images = sorted(Path("memes").glob("*"))
    MEMES_AND_COPYPASTAS["memes"] = meme_images
    MEMES_AND_COPYPASTAS["copypastas"] = copypastas


load_copypastas()


@discord_client.event
async def on_ready():
    print(f"Logged in as {discord_client.user}")


def is_past_cooldown(guild_id: int) -> bool:
    last_timestamp = LAST_TIMESTAMPS.get(
        guild_id, datetime.datetime.utcfromtimestamp(0)
    )
    cur_time = datetime.datetime.utcnow()
    time_diff = (datetime.datetime.utcnow() - last_timestamp).total_seconds()
    if time_diff < COOLDOWN:
        return False
    LAST_TIMESTAMPS[guild_id] = cur_time
    return True


def is_sticker(message: discord.Message) -> bool:
    return len(message.stickers) > 0


def is_url(message: discord.Message) -> bool:
    validation = validators.url(message.content, public=True)
    return isinstance(validation, bool)


def is_attachment(message: discord.Message) -> bool:
    return len(message.attachments) > 0


def is_emoji(message: discord.Message) -> bool:
    return emoji.is_emoji(message.content)


def sub_all_emojis(content: str) -> str:
    content_sub_custom_emojis = emoji_regex.sub("", content)
    content_sub_all_emojis = [
        char for char in content_sub_custom_emojis if not emoji.is_emoji(char)
    ]
    content = "".join(content_sub_all_emojis)
    content = spaces_regex.sub("", content)
    return content


def sub_all_mentions(content: str) -> str:
    content_sub_mentions = mention_regex.sub("", content)
    content_sub_mentions = spaces_regex.sub("", content_sub_mentions)
    return content_sub_mentions


async def on_cape_message(message: discord.Message):
    if "cape" not in [role.name for role in message.author.roles]:  # type:ignore
        return await message.delete()
    if is_sticker(message) or is_url(message):
        return
    if is_attachment(message) and message.content in ("", "cape"):
        return
    if is_emoji(message):
        return
    content = sub_all_emojis(message.content)
    content = sub_all_mentions(content)
    if content not in ("", "cape"):
        return await message.delete()


async def random_cape_message(message: discord.Message):
    if not is_past_cooldown(message.guild.id):  # type: ignore
        return
    # message_choices: list[str | Path] = [
    #     *MEMES_AND_COPYPASTAS["memes"],
    #     *MEMES_AND_COPYPASTAS["copypastas"],
    # ]
    contexts: list = []
    if str(message.author) == "sc#6792":
        contexts.append("kiseki")
    if solve_south_context.search(message.content):
        contexts.append("solvesouth")
    if cheese_context.search(message.content):
        contexts.append("cheese")
    if shitter_context.search(message.content):
        contexts.append("shitter")
    cape_role = discord.utils.get(message.guild.roles, name="cape")  # type: ignore
    if cape_role and len(contexts) == 0:
        cape_role_id = cape_role.id
        if message.author.get_role(cape_role_id) is not None:  # type: ignore
            contexts.append("cape")
        else:
            contexts.append("nocape")
    message_choices: list[str] = []
    for copypasta in MEMES_AND_COPYPASTAS["copypastas"]:
        if any(dup in copypasta["contexts"] for dup in contexts):
            message_choices.append(copypasta["text"])
    message_choice = random.choice(message_choices)
    if not message_choice.startswith("IMAGE:"):
        copypasta = re.sub(r"%USERNAME%", message.author.mention, message_choice)
        return await message.channel.send(copypasta)
    image_path = Path("memes") / message_choice.split("IMAGE:")[1]
    discord_file = discord.File(image_path)
    embed = discord.Embed(title="cape", type="image")
    embed.set_image(url=f"attachment://{discord_file.filename}")
    return await message.channel.send(embed=embed, file=discord_file)


async def translate_message(message: discord.Message):
    content: t.List[str] = message.content.split(" ", 1)
    if len(content) == 1 and content[0] == "$translate":
        return await help_text(message.channel)
    text = content[1]
    fuckery = DEFAULT_FUCKERY
    if text.startswith(COMMAND_PREFIX):
        command = text[1:]
        if command == "help":
            return await help_text(message.channel)
        if command.startswith("fuckery"):
            subcommand = command.split(" ", 2)
            if len(subcommand) <= 2:
                print("No subcommand provided")
                return await invalid_fuckery(message.channel)
            try:
                fuckery = int(subcommand[1])
                if not 0 <= fuckery <= MAX_FUCKERY:
                    raise ValueError("Fuckery not in valid range")
            except ValueError:
                return await invalid_fuckery(message.channel)
            text = subcommand[2]
        else:
            return await help_text(message.channel, messed_up=True)
    if len(text) > MAX_CHARS:
        return await text_too_long(message.channel, len(text))
    if read_translation_chars() + len(text) * (fuckery + 1) >= TRANSLATION_QUOTA:
        return await rate_limit(message.channel)
    if not is_past_cooldown(message.guild.id):  # type: ignore
        return
    input_language = "en"
    output_language = "en"
    for i in range(1, fuckery + 1):
        if i % 6 == 0 and i <= fuckery:
            print(f"Translating from {output_language} to en")
            text = await translate_text(message.channel, text, output_language, "en")
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
    return await message.channel.send(text)


@discord_client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author == discord_client.user:
        return
    if before.channel.name == "cape":  # type: ignore
        return await on_cape_message(after)


@discord_client.event
async def on_message(message: discord.Message):
    if message.author == discord_client.user:
        return
    if message.channel.name == "cape":  # type: ignore
        return await on_cape_message(message)
    if message.content.startswith(BOT_PREFIX):
        if message.content == f"{BOT_PREFIX} -reload":
            load_copypastas()
            return await message.channel.send("Reloaded!")
        return await translate_message(message)
    if cape_regex.search(message.content):
        return await random_cape_message(message)


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
        with open(LOG_FILE, "w", encoding="UTF-8") as chars_log:
            chars_log.write("0")


def add_translation_chars(num_chars: int) -> None:
    with open(LOG_FILE, "r+", encoding="UTF-8") as chars_log:
        num_translation_chars = int(chars_log.read()) + num_chars
        chars_log.seek(0)
        chars_log.write(str(num_translation_chars))
        chars_log.truncate()


def read_translation_chars() -> int:
    with open(LOG_FILE, "r", encoding="UTF-8") as chars_log:
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
