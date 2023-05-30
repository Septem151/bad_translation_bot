import random
import re

from google.cloud.translate_v2 import Client

DEFAULT_LANG: dict[str, str] = {
    "language": "en",
    "name": "English",
}

LANGS: list[dict[str, str]] = [
    {"language": "af", "name": "Afrikaans"},
    {"language": "sq", "name": "Albanian"},
    {"language": "am", "name": "Amharic"},
    {"language": "ar", "name": "Arabic"},
    {"language": "hy", "name": "Armenian"},
    {"language": "az", "name": "Azerbaijani"},
    {"language": "eu", "name": "Basque"},
    {"language": "be", "name": "Belarusian"},
    {"language": "bn", "name": "Bengali"},
    {"language": "bs", "name": "Bosnian"},
    {"language": "bg", "name": "Bulgarian"},
    {"language": "ca", "name": "Catalan"},
    {"language": "ceb", "name": "Cebuano"},
    {"language": "ny", "name": "Chichewa"},
    {"language": "zh", "name": "Chinese (Simplified)"},
    {"language": "zh-TW", "name": "Chinese (Traditional)"},
    {"language": "co", "name": "Corsican"},
    {"language": "hr", "name": "Croatian"},
    {"language": "cs", "name": "Czech"},
    {"language": "da", "name": "Danish"},
    {"language": "nl", "name": "Dutch"},
    {"language": "en", "name": "English"},
    {"language": "eo", "name": "Esperanto"},
    {"language": "et", "name": "Estonian"},
    {"language": "tl", "name": "Filipino"},
    {"language": "fi", "name": "Finnish"},
    {"language": "fr", "name": "French"},
    {"language": "fy", "name": "Frisian"},
    {"language": "gl", "name": "Galician"},
    {"language": "ka", "name": "Georgian"},
    {"language": "de", "name": "German"},
    {"language": "el", "name": "Greek"},
    {"language": "gu", "name": "Gujarati"},
    {"language": "ht", "name": "Haitian Creole"},
    {"language": "ha", "name": "Hausa"},
    {"language": "haw", "name": "Hawaiian"},
    {"language": "iw", "name": "Hebrew"},
    {"language": "hi", "name": "Hindi"},
    {"language": "hmn", "name": "Hmong"},
    {"language": "hu", "name": "Hungarian"},
    {"language": "is", "name": "Icelandic"},
    {"language": "ig", "name": "Igbo"},
    {"language": "id", "name": "Indonesian"},
    {"language": "ga", "name": "Irish"},
    {"language": "it", "name": "Italian"},
    {"language": "ja", "name": "Japanese"},
    {"language": "jw", "name": "Javanese"},
    {"language": "kn", "name": "Kannada"},
    {"language": "kk", "name": "Kazakh"},
    {"language": "km", "name": "Khmer"},
    {"language": "ko", "name": "Korean"},
    {"language": "ku", "name": "Kurdish (Kurmanji)"},
    {"language": "ky", "name": "Kyrgyz"},
    {"language": "lo", "name": "Lao"},
    {"language": "la", "name": "Latin"},
    {"language": "lv", "name": "Latvian"},
    {"language": "lt", "name": "Lithuanian"},
    {"language": "lb", "name": "Luxembourgish"},
    {"language": "mk", "name": "Macedonian"},
    {"language": "mg", "name": "Malagasy"},
    {"language": "ms", "name": "Malay"},
    {"language": "ml", "name": "Malayalam"},
    {"language": "mt", "name": "Maltese"},
    {"language": "mi", "name": "Maori"},
    {"language": "mr", "name": "Marathi"},
    {"language": "mn", "name": "Mongolian"},
    {"language": "my", "name": "Myanmar (Burmese)"},
    {"language": "ne", "name": "Nepali"},
    {"language": "no", "name": "Norwegian"},
    {"language": "ps", "name": "Pashto"},
    {"language": "fa", "name": "Persian"},
    {"language": "pl", "name": "Polish"},
    {"language": "pt", "name": "Portuguese"},
    {"language": "pa", "name": "Punjabi"},
    {"language": "ro", "name": "Romanian"},
    {"language": "ru", "name": "Russian"},
    {"language": "sm", "name": "Samoan"},
    {"language": "gd", "name": "Scots Gaelic"},
    {"language": "sr", "name": "Serbian"},
    {"language": "st", "name": "Sesotho"},
    {"language": "sn", "name": "Shona"},
    {"language": "sd", "name": "Sindhi"},
    {"language": "si", "name": "Sinhala"},
    {"language": "sk", "name": "Slovak"},
    {"language": "sl", "name": "Slovenian"},
    {"language": "so", "name": "Somali"},
    {"language": "es", "name": "Spanish"},
    {"language": "su", "name": "Sundanese"},
    {"language": "sw", "name": "Swahili"},
    {"language": "sv", "name": "Swedish"},
    {"language": "tg", "name": "Tajik"},
    {"language": "ta", "name": "Tamil"},
    {"language": "te", "name": "Telugu"},
    {"language": "th", "name": "Thai"},
    {"language": "tr", "name": "Turkish"},
    {"language": "uk", "name": "Ukrainian"},
    {"language": "ur", "name": "Urdu"},
    {"language": "uz", "name": "Uzbek"},
    {"language": "vi", "name": "Vietnamese"},
    {"language": "cy", "name": "Welsh"},
    {"language": "xh", "name": "Xhosa"},
    {"language": "yi", "name": "Yiddish"},
    {"language": "yo", "name": "Yoruba"},
    {"language": "zu", "name": "Zulu"},
]

EXCLUDE_LANGS: list[dict[str, str]] = [
    {"language": "eo", "name": "Esperanto"},
    {"language": "si", "name": "Sinhala"},
    {"language": "id", "name": "Indonesian"},
    {"language": "mi", "name": "Maori"},
    {"language": "nl", "name": "Dutch"},
    {"language": "fr", "name": "French"},
]

DEFAULT_NUM_TRANSLATIONS: int = 5


class Translator:
    def __init__(
        self, source: str, client: Client, source_lang: dict[str, str] | None = None
    ) -> None:
        self.client: Client = client
        if not source_lang:
            source_lang = DEFAULT_LANG
        self.source: str = source
        self.result: str = source
        self.used: list[dict[str, str]] = [source_lang]
        self.lang: dict[str, str] | None = source_lang
        self.last_lang: dict[str, str] | None = None
        self.next: list[dict[str, str] | None] = [
            None,
        ]
        self.rand = random.Random()

    def __setrandomlang(self) -> None:
        while not self.lang or self.lang in self.used or self.lang in EXCLUDE_LANGS:
            self.lang = self.rand.choice(LANGS)

    def __translate(self, lang: dict[str, str] | None = None) -> None:
        if lang:
            self.lang = lang
        elif self.next:
            self.lang = self.next.pop()
            if not self.lang:
                self.__setrandomlang()
        else:
            self.__setrandomlang()

        done = False
        while not done:
            try:
                translation = {}
                if self.lang is not None:
                    if self.last_lang is not None:
                        translation = self.client.translate(
                            self.result,
                            target_language=self.lang["language"],
                            source_language=self.last_lang["language"],
                        )
                    else:
                        translation = self.client.translate(
                            self.result,
                            target_language=self.lang["language"],
                        )
            except Exception as exception:
                print("Exception failed")
                continue
            done = True

        self.result = translation["translatedText"]
        self.result = self.result.replace("&#39;", "'")
        self.result = self.result.replace("&quot;", '"')
        self.last_lang = self.lang
        if self.lang is not None:
            self.used += [self.lang]

    def translate(self, num_translations: int = DEFAULT_NUM_TRANSLATIONS) -> str:
        for _ in range(0, num_translations):
            self.__translate()
        self.__translate(DEFAULT_LANG)

        endings = [
            ".",
            ",",
            "!",
            "?",
            ":",
            ";",
        ]

        if self.source.endswith(".") and not any(
            self.result.endswith(ending) for ending in endings
        ):
            self.result = self.result + "."

        if self.source.endswith("-") and not self.result.endswith("-"):
            if self.result.endswith("."):
                self.result = self.result[:-1]
            self.result = self.result + "-"

        if self.source.endswith("!") and not self.result.endswith("!"):
            if any(self.result.endswith(punc) for punc in [".", ",", ":", ";"]):
                self.result = self.result[:-1]
            self.result = self.result + "!"

        if self.source.endswith("?") and not self.result.endswith("?"):
            if any(self.result.endswith(punc) for punc in [".", ",", ":", ";"]):
                self.result = self.result[:-1]
            self.result = self.result + "?"

        if self.source[:1].isupper():
            self.result = re.sub(
                "^([a-zA-Z])", lambda x: x.groups()[0].upper(), self.result, 1
            )
        else:
            self.result = re.sub(
                "^([a-zA-Z])", lambda x: x.groups()[0].lower(), self.result, 1
            )

        return self.result
