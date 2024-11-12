FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && apt-get install -y \
    iputils-ping \
    traceroute \
    net-tools \
    curl \
    vim \
    nginx \
    sudo \
    && apt-get clean

# Create a new user 'user' and set up their environment
RUN useradd -m user && echo "user:user" | chpasswd && usermod -aG sudo user

# Copy custom bashrc for root and the new user
COPY bashrc /root/.bashrc
COPY bashrc /home/user/.bashrc
RUN chown user:user /home/user/.bashrc

# Copy nginx configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY sites-available/* /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/shopping_site /etc/nginx/sites-enabled/
RUN ln -s /etc/nginx/sites-available/blog_site /etc/nginx/sites-enabled/

# Copy website files
COPY shopping_site/ /var/www/shopping_site/
COPY blog_site/ /var/www/blog_site/

# Expose ports
EXPOSE 80
EXPOSE 8080

# Add the agent start script
COPY start_agent.sh /usr/local/bin/start_agent.sh
RUN chmod +x /usr/local/bin/start_agent.sh


# Start agent and nginx
CMD ["/bin/bash", "-c", "/usr/local/bin/start_agent.sh"]