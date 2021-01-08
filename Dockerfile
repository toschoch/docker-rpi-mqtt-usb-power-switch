FROM balenalib/raspberrypi3-python:run
RUN install_packages uhubctl
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY subscribe.py ./

CMD python subscribe.py