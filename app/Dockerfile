FROM python:3.9.7-alpine3.14

ENV TODO /todo-list
WORKDIR $TODO

COPY . . 

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
