FROM python:3.9-bullseye
WORKDIR /app

# Copy files to docker
COPY main.py main.py
COPY cookies_jar.json cookies_jar.json
COPY requirements.txt requirements.txt

# download Chrome
RUN apt-get update
RUN apt-get install -y wget
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install --fix-broken
RUN dpkg --configure -a
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# python install package
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
ENV DISPLAY=:99
CMD ["python3", "main.py"]