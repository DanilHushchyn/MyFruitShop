# pull official base image
FROM python:3.10-alpine

# set work directory
WORKDIR /usr/src/MyFruitShop

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
RUN apk --update --upgrade --no-cache add fontconfig ttf-freefont font-noto terminus-font \
   && fc-cache -f \
   && fc-list | sort

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN apk add py3-pip py3-pillow py3-cffi py3-brotli gcc musl-dev python3-dev pango


# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/MyFruitShop/entrypoint.sh
RUN chmod +x /usr/src/MyFruitShop/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/MyFruitShop/entrypoint.sh"]
