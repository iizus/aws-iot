FROM python


RUN apt update
RUN apt upgrade -y
RUN apt install -y cmake

RUN pip install -U pip
RUN pip install awsiotsdk