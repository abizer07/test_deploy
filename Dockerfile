# Use official Python slim image
FROM python:3.11-slim


# create working dir
WORKDIR /usr/src/app


# install build deps and then remove cache
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
&& rm -rf /var/lib/apt/lists/*


# copy requirements first (for docker cache)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


# copy app code
COPY . .


EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]