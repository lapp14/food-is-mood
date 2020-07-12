FROM python:3.7-alpine
WORKDIR /code

RUN apk add --no-cache gcc musl-dev linux-headers
COPY ./food-is-mood/ .

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 pip install -e . && \
 pip install -e ".[dev]" && \
 apk --purge del .build-deps


CMD ["pserve", "dev.ini", "--reload"]
