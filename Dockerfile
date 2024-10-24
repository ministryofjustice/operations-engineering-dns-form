FROM python:3.12.0-alpine3.18

LABEL maintainer="operations-engineering <operations-engineering@digital.justice.gov.uk>"

RUN addgroup -S appgroup && adduser -S appuser -G appgroup -u 1051

RUN apk add --no-cache --no-progress \
  libffi-dev \
  build-base \
  curl \
  && apk update \
  && apk upgrade --no-cache --available

WORKDIR /home/operations-engineering-dns-form

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY app app

RUN pip3 install --no-cache-dir pipenv==2024.1.0 \
  && pipenv install --system --deploy --ignore-pipfile

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

USER 1051

EXPOSE 4567

HEALTHCHECK --interval=60s --timeout=30s CMD curl -I -XGET http://localhost:4567 || exit 1

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:4567", "app.run:app()"]
