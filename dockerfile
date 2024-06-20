FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_ENV=production

# ENV ENV_VAR_NAME=value

EXPOSE 80

# Run your application (replace with your actual cx1ommand)
CMD ["gunicorn", "--bind", "0.0.0.0:80", "wsgi:app"]