FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH /usr/local/bin:$PATH

WORKDIR /app
ADD . /app

# Install required packages, add the PPA repository, and install Python 3.11, and other packages
RUN set -xe \
    && apt-get update -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
        python3-pip \
        gdal-bin \
        libgdal-dev

# Copy requirements.txt and GDAL wheel file to the container
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install --upgrade numpy pandas

COPY . .
