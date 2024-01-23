FROM python:3.9-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    libgl1-mesa-glx \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/open-mmlab/mmcv.git && \
    cd mmcv && \
    pip install -r requirements/optional.txt && \
    MMCV_WITH_OPS=1 pip install -e .

RUN git clone https://github.com/open-mmlab/mmdetection.git && \
    cd mmdetection && pip install -e .

COPY . .
