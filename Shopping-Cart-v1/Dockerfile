# init a base image (Alpine is small Linux distro)
#FROM python:3.6.1-alpine
FROM python:3.6.8-alpine3.8
# define the present working directory
WORKDIR /Shopping-Cart-v1
# copy the contents into the working dir
ADD . /Shopping-Cart-v1
# run pip to install the dependencies of the flask app
RUN pip install -r requirements.txt
# define the command to start the container
CMD ["python","app.py"]