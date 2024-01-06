FROM python:3.11

# Install pre-requirements
RUN pip install pip~=23.3.2 setuptools~=69.0.3

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY ./local_app /src/local_app
WORKDIR /src/local_app
CMD ["flask", "run", "--host", "0.0.0.0"]