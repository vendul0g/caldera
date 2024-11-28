FROM ubuntu:24.04
SHELL ["/bin/bash", "-c"]

ARG TZ="UTC"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

WORKDIR /usr/src/app

# Clone check for recursive download
ADD . .
RUN if [ -z "$(ls plugins/stockpile)" ]; then \
    echo "stockpile plugin not downloaded - please ensure you recursively cloned the caldera git repository and try again."; \
    exit 1; \
fi

RUN apt-get update && \
    apt-get -y install python3 python3-pip python3-venv git curl golang-go && \
    echo "Base packages installed successfully."

# Handle optional mingw-w64 installation
ARG WIN_BUILD=false
RUN if [ "$WIN_BUILD" = "true" ] ; then \
    apt-get -y install mingw-w64 && \
    echo "mingw-w64 installed for Windows build."; \
fi

# Set up Python virtual environment
ENV VIRTUAL_ENV=/opt/venv/caldera
RUN python3 -m venv $VIRTUAL_ENV && \
    echo "Python virtual environment created at $VIRTUAL_ENV."
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt && \
    echo "Python dependencies installed."

# Set up local configuration
RUN python3 -c "import app; import app.utility.config_generator; app.utility.config_generator.ensure_local_config();" && \
    sed -i '/\- atomic/d' conf/local.yml && \
    echo "Local configuration set."

# Compile default Sandcat agent binaries
WORKDIR /usr/src/app/plugins/sandcat/gocat
RUN go mod tidy && go mod download && \
    echo "Go dependencies for Sandcat agent installed."

WORKDIR /usr/src/app/plugins/sandcat
RUN ./update-agents.sh && \
    echo "Sandcat agents updated."

# Test gocat extensions
RUN mkdir /tmp/gocatextensionstest && \
    cp -R ./gocat /tmp/gocatextensionstest/gocat && \
    cp -R ./gocat-extensions/* /tmp/gocatextensionstest/gocat/ && \
    cp ./update-agents.sh /tmp/gocatextensionstest/update-agents.sh && \
    cd /tmp/gocatextensionstest && \
    mkdir /tmp/gocatextensionstest/payloads && \
    ./update-agents.sh && \
    echo "gocat extensions compiled successfully."

# Clone Atomic Red Team repository for the Atomic plugin
RUN if [ ! -d "/usr/src/app/plugins/atomic/data/atomic-red-team" ]; then \
    git clone --depth 1 https://github.com/redcanaryco/atomic-red-team.git \
        /usr/src/app/plugins/atomic/data/atomic-red-team && \
    echo "Atomic Red Team repository cloned."; \
fi

# Install Node.js, npm, and build Vue frontend with logs
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    echo "Node.js and npm installed." && \
    if [ -d "plugins/magma" ]; then \
        cd plugins/magma && \
        npm install && echo "npm dependencies installed for Magma plugin." && \
        npm run build && echo "Magma plugin Vue components built."; \
    else \
        echo "Magma plugin not found, skipping build."; \
    fi && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    echo "Cleaned up unnecessary packages."


WORKDIR /usr/src/app

STOPSIGNAL SIGINT

# Expose necessary ports
EXPOSE 8888 8443 7010 7011/udp 7012 8853 8022 2222

ENTRYPOINT ["python3", "server.py"]
