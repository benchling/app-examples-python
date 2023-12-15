FROM python:3.11

COPY . /src/app

RUN python -m pip install pip-tools

WORKDIR /src/app

# Use bash for source
SHELL ["/bin/bash", "-c"]
RUN python3 -m venv .venv
RUN source .venv/bin/activate
RUN pip-compile -o requirements.txt pyproject.toml
RUN pip install -r requirements.txt

WORKDIR /src/app/local_app

# Don't use --debug in production!
CMD ["flask", "run", "--host", "0.0.0.0", "--debug"]