FROM python:3.11.9-alpine
LABEL authors="csmith"
WORKDIR /usr/local/app

ENV VAULT_ADDR=""
ENV VAULT_TOKEN=""

COPY Pipfile ./
COPY Pipfile.lock ./
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

COPY main.py main.py
COPY vault_api.py vault_api.py
COPY kmip.py kmip.py
COPY misc_utils.py misc_utils.py

CMD ["pipenv", "run", "python", "main.py", "--kmip"]
