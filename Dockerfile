FROM debian:buster
LABEL maintainer="Abhishek N. Kulkarni" \
        email="abhi.bp1993@gmail.com" \
        version="0.1.0" \
        project="spotondocker"

# Install python and spot
# Reference: https://gitlab.lrde.epita.fr/spot/spot-web/-/blob/master/docker/Dockerfile
RUN echo 'deb [trusted=true] http://www.lrde.epita.fr/repo/debian/ stable/' >> /etc/apt/sources.list && \
    apt-get update && \
    RUNLEVEL=1 DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --allow-unauthenticated --no-install-recommends \
    build-essential spot libspot-dev spot-doc python3-spot python3-pip python3-setuptools python3-dev && \
    apt-get clean

# Install python packages
RUN pip3 install pyzmq pydot networkx thrift

# Create folder for mapping code to docker
RUN mkdir /home/spotondocker
COPY spotondocker/genpy/ /home/spotondocker/genpy/
COPY spotondocker/server.py /home/spotondocker/
WORKDIR /home/spotondocker/