FROM ubuntu:latest
RUN apt-get update -y
RUN pip install -r requirements.txt
ENTRYPOINT [ "executable" ]
CMD ["server.py"]