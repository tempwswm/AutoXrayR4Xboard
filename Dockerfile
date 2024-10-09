FROM python:3.12-slim-bullseye
ENV TZ=Asia/Shanghai
WORKDIR /root/run
COPY src/requirements.txt /root/run/
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /root/run/


ENTRYPOINT ["python","-u", "main.py"]