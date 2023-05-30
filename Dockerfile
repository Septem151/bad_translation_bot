FROM python:3.11.3

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock .env key_file.json ./
COPY bad_translation_bot/ ./bad_translation_bot
RUN pip install --no-cache-dir poetry \
  && poetry config virtualenvs.create false
RUN poetry install --without dev --no-interaction --no-ansi \
  && pip cache purge

CMD [ "python", "./bad_translation_bot/__init__.py" ]
