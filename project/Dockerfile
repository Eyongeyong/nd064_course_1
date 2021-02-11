FROM python:2.7
LABEL maintainer = "Eyong Eyong" 

COPY ./techtrends /techtrends
WORKDIR /techtrends

RUN pip install -r requirements.txt
EXPOSE 3111

CMD python init_db.py ; python app.py