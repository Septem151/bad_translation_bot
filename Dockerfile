FROM python:3.10.5

WORKDIR /usr/src/app

COPY ./pyproject.toml ./.env ./key_file.json .
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root --no-interaction --no-ansi \
    && pip cache purge

CMD [ "python", "./bad_translation_bot/__init__.py" ]
