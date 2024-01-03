FROM python:3.11

COPY pip_requirements.txt ./

RUN pip install -r pip_requirements.txt
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY ./local_app /src/local_app
WORKDIR /src/local_app
CMD ["flask", "run", "--host", "0.0.0.0"]