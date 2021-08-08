FROM python:3.8

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root --no-interaction --no-ansi \
    && pip cache purge

CMD [ "python", "./bad_translation_bot/__init__.py" ]
