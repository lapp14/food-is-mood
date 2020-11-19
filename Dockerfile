FROM python:3.8.6-alpine
WORKDIR /app
ADD . /app

ENV PYTHONPATH "${PYTHONPATH}:./recipes/"
ENV AWS_S3_BUCKET_NAME="food-is-mood"
ENV AWS_S3_BUCKET_URL="https://food-is-mood.s3.us-east-2.amazonaws.com/"
ENV AWS_S3_BASE_PATH="dev/"
ENV AWS_S3_BASE_URL="https://food-is-mood.s3.us-east-2.amazonaws.com/"
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

RUN pip install -r requirements.txt
CMD pserve prod.ini --reload

