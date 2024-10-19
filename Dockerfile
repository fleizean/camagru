# Dockerfile
FROM python:3.11-alpine

ENV PIP_ROOT_USER_ACTION=ignore \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
    #PIP_NO_CACHE_DIR=off 

# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt /camagru/requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install --upgrade pip && pip install -r /camagru/requirements.txt

# After the packages are installed, copy the rest of your application
COPY camagru /camagru

RUN chmod +x /camagru/start.sh

WORKDIR /camagru

EXPOSE 8001

CMD [ "sh", "/camagru/start.sh" ]

