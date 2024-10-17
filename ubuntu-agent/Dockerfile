# ubuntu-agent-1/Dockerfile and ubuntu-agent-2/Dockerfile
FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && apt-get install -y \
    iputils-ping \
    traceroute \
    net-tools \
    curl \
    vim \
    && apt-get clean

# Create a new user 'user' and set up their environment
RUN useradd -m user && echo "user:user" | chpasswd && usermod -aG sudo user

# Copy custom bashrc for root and the new user
COPY bashrc /root/.bashrc
COPY bashrc /home/user/.bashrc
RUN chown user:user /home/user/.bashrc

# Keeps the container running
CMD ["tail", "-f", "/dev/null"]
