FROM python:3.11

COPY pip_requirements.txt ./

RUN python -r install pip_requirements.txt

COPY ./local_app /src/local_app
RUN pip install -r requirements.txt
WORKDIR /src/local_app
CMD ["flask", "run", "--host", "0.0.0.0"]