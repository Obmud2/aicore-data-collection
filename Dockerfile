# 
FROM python:3.8

RUN apt-get -y update
RUN apt -y upgrade
RUN apt-get install -y gnupg2 && apt-get install -y wget

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update
RUN apt-get install -y google-chrome-stable

RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/ -S chromedriver.storage.googleapis.com/LATEST_RELEASE/chromedriver_linux64.zip
RUN apt-get install -y unzip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# COPY . .
# RUN pip install -r requirements.txt && pip install .
# CMD ["python", "scraper"]