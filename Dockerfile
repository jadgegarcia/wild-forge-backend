FROM python:3.11

# Set the working directory to /app
WORKDIR /app

# Copy only the requirements file first for caching purposes
COPY ./requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory (including manage.py)
COPY ./backend /app/

# Copy the entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Use CMD to specify the command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
