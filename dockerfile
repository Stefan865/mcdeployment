FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code into the container at /app
COPY . /app

# Define environment variables if needed
# ENV ENV_VAR_NAME=value

EXPOSE 80

# Run your application (replace with your actual cx1ommand)
CMD ["flask", "run"]