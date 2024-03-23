# Get python 3.11 image
FROM python:3.11

# Create the directory /app
RUN mkdir /app

# Copy the current directory contents into the container at /app
COPY app.py /app/app.py
COPY static /app/static
COPY requirements.txt /app/requirements.txt

# Set the working directory
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8000

# # Define environment variable
# ENV DETECT_URL=$DETECT_URL
# ENV GET_IMAGE_URL=$GET_IMAGE_URL
# ENV GET_IMAGES_URL=$GET_IMAGEs_URL

# Run app.py when the container launches
CMD ["python", "app.py"]
