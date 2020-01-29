FROM python:3


RUN apt-get update \
            && apt-get install -y --no-install-recommends \
               nginx \
               gettext-base \
            && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip


ENV PYTHONUNBUFFERED 1
ENV STATIC_FILE_ROOT=/var/www


WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt


# Send nginx logs to stdout/stderr so they show up in docker logs
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log
# Move nginx config into place
COPY ./nginx.conf.template .
RUN envsubst '${STATIC_FILE_ROOT}' < ./nginx.conf.template > /etc/nginx/nginx.conf


COPY . .

# Move django static files to the location Nginx expects them
RUN python manage.py collectstatic --no-input


EXPOSE 80
# This default command is suitable for development testing
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
