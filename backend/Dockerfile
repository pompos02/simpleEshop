FROM python:3.10-slim

# Copy requirements.txt from the root 
COPY requirements.txt /requirements.txt

# install the requirements
RUN pip install --no-cache-dir -r /requirements.txt

# copy all the backend files
COPY backend/ .

# copy the web files
COPY web/templates ./web/templates
COPY web/static ./web/static

# start the app
CMD ["python", "app.py"]
