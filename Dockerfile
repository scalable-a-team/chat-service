# start by pulling the python image
FROM python:3.8

# copy the requirements file into the image
COPY ./apis/requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY ./apis /app

# configure the container to run in an executed manner
ENTRYPOINT [ "opentelemetry-instrument", "python" ]

CMD ["app.py" ]
# FROM python:3.7-alpine

# COPY ./apisrequirements.txt /app/requirements.txt

# RUN pip install -r /app/requirements.txt

# COPY ./apis /app
# WORKDIR /app
# RUN mkdir ./static/
# CMD ["python", "app.py"]