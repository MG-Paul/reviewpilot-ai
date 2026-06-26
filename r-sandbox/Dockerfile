FROM r-base:4.3.2

# Install system dependencies for R packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libsodium-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Install standard R packages for meta-analysis
RUN R -e "install.packages(c('plumber', 'meta', 'metafor', 'jsonlite'), repos='https://cloud.r-project.org/')"

# Copy Plumber script
COPY server.R /usr/src/app/

EXPOSE 8000

# Start Plumber server
CMD ["R", "-e", "pr <- plumber::plumb('server.R'); pr\$run(host='0.0.0.0', port=8000)"]
