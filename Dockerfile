FROM python

# Update
RUN apt update
RUN apt upgrade -y

# Install Device SDK
RUN apt install -y cmake
RUN pip install -U pip
RUN pip install awsiotsdk

# For launch client
RUN apt install -y jq