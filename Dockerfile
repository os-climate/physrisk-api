FROM registry.access.redhat.com/ubi8/ubi-minimal

# Create working directory
RUN mkdir -p /usr/local/src/app
# Add source(s)
COPY . /usr/local/src/app
# Enter working directory
WORKDIR /usr/local/src/app

# Install
RUN \
    # Install shadow-utils for adduser functionality
    microdnf -y install shadow-utils \
    # Install Python 3.9
    && microdnf -y install python38 \
    # Install application
    && pip3 install . \
    # Clean up unnecessary data
    && microdnf clean all && rm -rf /var/cache/yum

# Run as non-root user
RUN adduser physrisk-api
USER physrisk-api

# Enable communication via port 8081
EXPOSE 8081

# Run application
CMD ["waitress-serve", "--port=8081", "--call", "src.physrisk_api.app:create_app"]
