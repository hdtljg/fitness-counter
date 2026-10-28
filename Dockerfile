# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Optional mirrors for users with slow access to Debian/PyPI.
# Example:
#   docker build \
#     --build-arg APT_MIRROR_HOST=mirrors.tuna.tsinghua.edu.cn \
#     --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
#     -t fitness-counter .
ARG APT_MIRROR_HOST=deb.debian.org
ARG PIP_INDEX_URL=https://pypi.org/simple

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

# OpenCV / MediaPipe runtime libraries. The image is intended for video-file
# processing; webcam input is only supported when running natively.
RUN set -eux; \
    if [ "${APT_MIRROR_HOST}" != "deb.debian.org" ]; then \
        if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
            sed -i "s|deb.debian.org|${APT_MIRROR_HOST}|g" /etc/apt/sources.list.d/debian.sources; \
        fi; \
        if [ -f /etc/apt/sources.list ]; then \
            sed -i "s|deb.debian.org|${APT_MIRROR_HOST}|g" /etc/apt/sources.list; \
        fi; \
    fi; \
    apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgomp1 \
        libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --index-url "${PIP_INDEX_URL}" -r requirements.txt

COPY code/ /app/
COPY samples/ /app/samples/

ENTRYPOINT ["python", "main.py"]
