FROM python:3.10

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libsm6 libxext6 libxrender-dev libgl1-mesa-glx libgl1-mesa-dev && \
    pip install opencv-python numpy matplotlib

WORKDIR /app
COPY . /app

CMD ["python", "main.py"]

