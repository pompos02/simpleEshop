FROM python:3.10-slim

# Copy requirements.txt from the root of the build context
COPY requirements.txt /requirements.txt

# Εγκατάσταση requirements
RUN pip install --no-cache-dir -r /requirements.txt

# Αντιγραφή των αρχείων του backend (όλα όσα είναι στο ίδιο επίπεδο με το Dockerfile)
COPY backend/ .

# Αντιγραφή των φακέλων του web
COPY web/templates ./web/templates
COPY web/static ./web/static

# Εκκίνηση Flask app
CMD ["python", "app.py"]
