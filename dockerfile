FROM python:3.8

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libsm6 libxext6 libxrender-dev libgl1-mesa-glx libgl1-mesa-dev git && \
    pip install opencv-python numpy matplotlib

# Fetch the latest commit from the docker-updates branch
RUN git fetch origin docker-updates && \
    git checkout docker-updates && \
    git pull origin docker-updates

WORKDIR /app

# Run the app.py script
CMD ["python", "app.py"]

# Add, commit, and push all new changes made by the container
RUN git add . && \
    git commit -m "Docker container changes" && \
    git push origin docker-updates
