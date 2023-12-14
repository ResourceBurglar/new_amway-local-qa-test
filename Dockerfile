FROM python:3.10.5

ADD .  /home/bespin-local-qa

WORKDIR /home/bespin-local-qa

RUN pip3 install -r /home/bespin-local-qa/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

CMD ["python", "/home/bespin-local-qa/api.py"]