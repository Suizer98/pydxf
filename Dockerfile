FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=/usr/local/bin:$PATH

# QCAD: place the Linux trial .run in the setup folder
# (download from https://www.qcad.org/en/download
ENV QCAD_HOME=/opt/qcadcam
ENV QT_QPA_PLATFORM=offscreen
ENV XDG_RUNTIME_DIR=/tmp/runtime-root

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies
RUN set -xe \
    && apt-get update -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3-pip \
        python3-dev \
        build-essential \
        gdal-bin \
        libgdal-dev \
        libx11-6 \
        libxext6 \
        libxrender1 \
        libglib2.0-0 \
        libdbus-1-3 \
        libfontconfig1 \
        libfreetype6 \
        libgl1 \
    && mkdir -p /tmp/runtime-root \
    && chmod 700 /tmp/runtime-root \
    && rm -rf /var/lib/apt/lists/*

# Install QCAD
COPY setup/qcadcam-3.32.6-trial-linux-qt5.14-x86_64.run /tmp/qcad.run
RUN set -xe \
    && chmod +x /tmp/qcad.run \
    && /tmp/qcad.run --target /opt/qcadcam --accept --noexec \
    && rm -f /tmp/qcad.run \
    && sed -i 's/-platform xcb/-platform offscreen/' /opt/qcadcam/qcad \
    && if head -1 /opt/qcadcam/dwg2dwg 2>/dev/null | grep -q '^#!'; then \
         sed -i 's/-platform xcb/-platform offscreen/' /opt/qcadcam/dwg2dwg; \
       fi \
    && test -x /opt/qcadcam/dwg2dwg

# COPY requirements.txt .
# RUN pip install --upgrade pip \
#     && pip install -r requirements.txt

COPY pyproject.toml uv.lock .
RUN uv sync --frozen --no-install-project --no-dev --python 3.11

COPY . .

# Place the virtual environment in the PATH
ENV PATH="/app/.venv/bin:$PATH"
