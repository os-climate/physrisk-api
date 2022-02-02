
####
# Simple Dockerfile to test image build and pushing
#
# Build the image with:
#
# docker build -f docker/Dockerfile -t physrisk-api .
#
# Then run the container using:
#
# docker run -i --rm -p 8081:8081 physrisk-api
####
FROM python:slim

WORKDIR /app

RUN python3 -m venv venv
RUN . venv/bin/activate

# optimize image caching
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8081
CMD [ "waitress-serve", "--port=8081", "app:app"]
