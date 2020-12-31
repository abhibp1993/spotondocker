FROM debian:buster
LABEL maintainer="Abhishek N. Kulkarni" \
        email="ankulkarni@wpi.edu" \
        version="0.2"

# Install python and spot
# Reference: https://gitlab.lrde.epita.fr/spot/spot-web/-/blob/master/docker/Dockerfile
RUN echo 'deb [trusted=true] http://www.lrde.epita.fr/repo/debian/ stable/' >> /etc/apt/sources.list && \
    apt-get update && \
    RUNLEVEL=1 DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --allow-unauthenticated --no-install-recommends \
    build-essential spot libspot-dev spot-doc python3-spot python3-pip python3-setuptools python3-dev \
    libgraphviz-dev && \
    apt-get clean

# Install python packages
RUN pip3 install pyzmq pydot networkx
RUN pip3 install --no-cache-dir pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"

# Create folder for mapping code to docker
RUN mkdir /home/server
