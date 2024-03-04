FROM nvidia/cuda:12.3.0-base-ubuntu22.04

# Build arguments
ARG YOUTUBE_API_KEY
ARG OPENAI_API_KEY
ARG GMAIL_TWOFACTOR
ARG STREAMLIT_PORT

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV GMAIL_TWOFACTOR=${GMAIL_TWOFACTOR}
ENV STREAMLIT_PORT=${STREAMLIT_PORT}

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
        git \
        ffmpeg \
        python3.11 \
        python3.11-venv

# Git clone the repository
RUN git clone https://github.com/zsolt-szekeres/youtube_news.git \
    && cd youtube_news \
    && git checkout main

# Set the working directory
WORKDIR /youtube_news

# Create python virtual environment
RUN python3.11 -m venv env \
    && . env/bin/activate \
    && pip install --upgrade pip==24.0 \
    && pip install --upgrade setuptools==69.1.0 \
    && pip install -r requirements_py3.11_noconda.txt

# Set the entrypoint
RUN echo '#!/bin/bash\n\
source env/bin/activate\n\
"$@"' > /entrypoint.sh \
&& chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
EXPOSE ${STREAMLIT_PORT}

