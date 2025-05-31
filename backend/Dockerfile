FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt from the root 
COPY requirements.txt /app/requirements.txt

# install the requirements
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy all the backend files
COPY backend/ /app/

# copy the web files
COPY web/templates /app/web/templates
COPY web/static /app/web/static

# start the app
CMD ["python", "app.py"]
