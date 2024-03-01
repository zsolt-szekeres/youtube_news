FROM nvidia/cuda:12.3.0-base-ubuntu22.04

# Install system dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ffmpeg \
        python3.11 \
        python3.11-venv \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /youtube_news

# Copy the requirements file
COPY requirements_py3.11_noconda.txt requirements_py3.11_noconda.txt

# Create python virtual environment
RUN python3.11 -m venv env \
    && . env/bin/activate \
    && pip install --upgrade --no-cache-dir pip==24.0 \
    && pip install --upgrade --no-cache-dir setuptools==69.1.0 \
    && pip install --no-cache-dir -r requirements_py3.11_noconda.txt

# Copy the source code
COPY . /youtube_news

# persist the output data
VOLUME /data

# Set the entrypoint: 
# - copy the config.json from /etc/config/config.json to /youtube_news/config.json and 
# - create output folders
# - activate the virtual environment
RUN echo '#!/bin/bash\n\
cp /etc/config/config.json /youtube_news/config.json\n\
mkdir -p /data/log /data/videos /data/backup /data/vector_store\n\
source /youtube_news/env/bin/activate\n\
"$@"' > /entrypoint.sh \
&& chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
EXPOSE 8501
