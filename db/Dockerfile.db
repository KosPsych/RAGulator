FROM neo4j:latest
RUN pip install flask==3.0.2 neo4j==5.17.0 gunicorn==21.2.0


COPY ./db_api.py ./db_api.py

COPY ./neo4j.conf /var/lib/neo4j/conf/neo4j.conf

CMD exec gunicorn --bind :80 --workers 1 --threads 8 db_api:app