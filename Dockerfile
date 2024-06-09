FROM python:3.12.0
WORKDIR /bot
COPY requirements.txt /bot/
COPY musics_save.pickle /bot/
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg
RUN chmod 777 musics_save.pickle
COPY . /bot/
CMD python main.py