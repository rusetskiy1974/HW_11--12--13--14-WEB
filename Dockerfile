FROM python:3.11

WORKDIR /fastapi_proj

RUN pip install poetry

COPY . /fastapi_proj

RUN poetry install

#CMD ["poetry", "run", "python", "main.py"]