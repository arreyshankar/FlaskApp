# Use the official Python image as a base image
FROM python:3.9-slim

RUN apt-get update && \
apt-get upgrade -y

RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick
RUN apt-get install -y --fix-missing \    
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libboost-all-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev
RUN apt-get install -y --fix-missing pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*


# Install DLIB
RUN mkdir -p /root/dlib
RUN git clone -b 'v19.24' --single-branch https://github.com/davisking/dlib.git /root/dlib/
RUN cd /root/dlib/ && \
    python3 setup.py install


# Install Flask
RUN cd ~ && \
    pip3 install flask flask-cors


# Install Face-Recognition Python Library
RUN cd ~ && \
    mkdir -p face_recognition && \
    git clone https://github.com/ageitgey/face_recognition.git face_recognition/ && \
    cd face_recognition/ && \
    pip3 install -r requirements.txt && \
    python3 setup.py install


# Set the working directory in the container
WORKDIR /app

# Copy the Flask application code into the container
COPY . .

# Install Flask and other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which the Flask app will run
EXPOSE 5000

# Command to run the Flask app when the container starts
CMD ["python", "app.py"]
