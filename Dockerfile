FROM python


ARG SDK="aws-iot-device-sdk-python-v2"
ARG REPO="https://github.com/aws/$SDK.git"


RUN apt update
RUN apt upgrade -y
RUN apt install -y cmake

RUN git clone $REPO

RUN pip install -U pip
RUN pip install ./$SDK