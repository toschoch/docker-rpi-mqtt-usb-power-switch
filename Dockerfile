FROM balenalib/raspberrypi3:run

RUN install-packages uhubctl

CMD uhubctl && uhubctl -l 1-1 -p 2 -a 0 && uhubctl