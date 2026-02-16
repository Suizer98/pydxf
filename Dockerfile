FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH /usr/local/bin:$PATH

WORKDIR /app

# Install required packages and build dependencies for LibreDWG
RUN set -xe \
    && apt-get update -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
        python3-pip \
        gdal-bin \
        libgdal-dev \
        git \
        build-essential \
        autoconf \
        automake \
        libtool \
        texinfo

# Build and install LibreDWG (provides dwg2dxf command)
RUN git clone --depth 1 https://github.com/LibreDWG/libredwg.git /tmp/libredwg \
    && cd /tmp/libredwg \
    && sh autogen.sh \
    && ./configure --disable-bindings \
    && make \
    && make install \
    && ldconfig \
    && rm -rf /tmp/libredwg

# Copy requirements.txt and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install --upgrade numpy pandas

COPY . .
