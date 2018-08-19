# Docker environment for ubuntu, conda, python3.6
#
# Usage:
#  * build the image:
#    coinbasepro-python$ docker build -t coinbasepro-python .
#  * start the image:
#    docker run -it coinbasepro-python

# Latest version of ubuntu
FROM ubuntu:16.04

# Install system packages
RUN apt-get update && \
    apt-get install -y wget git libhdf5-dev g++ graphviz openmpi-bin libgl1-mesa-glx bzip2

# Install conda
ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH

RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.2.12-Linux-x86_64.sh && \
    echo "c59b3dd3cad550ac7596e0d599b91e75d88826db132e4146030ef471bb434e9a *Miniconda3-4.2.12-Linux-x86_64.sh" | sha256sum -c - && \
    /bin/bash /Miniconda3-4.2.12-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda3-4.2.12-Linux-x86_64.sh && \
    echo export PATH=$CONDA_DIR/bin:'$PATH' > /etc/profile.d/conda.sh

# Install Python packages
ARG python_version=3.6

RUN conda install -y python=${python_version} && \
    pip install --upgrade pip

# Set coinbasepro-python code path
ENV CODE_DIR /code/coinbasepro-python

RUN mkdir -p $CODE_DIR
COPY . $CODE_DIR

RUN cd $CODE_DIR && \
    pip install cbpro
