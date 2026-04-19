# Use an official Python image as a base
FROM python:3.12-slim
ADD requirements.txt /tmp/requirements.txt
# Install the Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt jupyter notebook
