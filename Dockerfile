FROM ubuntu:20.04

ENV PATH /usr/local/bin:$PATH

WORKDIR /app
ADD . /app

# Install required packages, add the PPA repository, and install Python 3.11, and other packages
RUN set -xe \
    && apt-get update -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
        wget \
        build-essential \
        libncursesw5-dev \
        libssl-dev \
        libsqlite3-dev \
        tk-dev \
        libgdbm-dev \
        libc6-dev \
        libbz2-dev \
        libffi-dev \
        zlib1g-dev \
    && add-apt-repository ppa:deadsnakes/ppa -y \
        python3.11

# Copy requirements.txt and GDAL wheel file to the container
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
