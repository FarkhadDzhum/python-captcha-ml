FROM tiangolo/uwsgi-nginx-flask:python3.6
RUN curl google.com
RUN apt-get update
RUN apt-get install -y libgl1-mesa-glx
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY /app /app