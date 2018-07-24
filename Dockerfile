FROM python:3.6-alpine3.7

ADD --chown=nobody:nobody requirements.txt demo.py /app/
ADD --chown=nobody:nobody templates /app/templates/
WORKDIR /app
RUN pip install -r requirements.txt

ENV FLASK_APP demo.py

USER nobody
ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]