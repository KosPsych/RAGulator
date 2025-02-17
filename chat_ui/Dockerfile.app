# This sets up the container with Python 3.10 installed.
FROM python:3.10-slim

# This copies everything in your current directory to the /app directory in the container.
COPY . /app

# This sets the /app directory as the working directory for any RUN, CMD, ENTRYPOINT, or COPY instructions that follow.
WORKDIR /app

# This runs pip install for all the packages listed in your requirements.txt file.
# streamlit==1.41.1
RUN pip install streamlit==1.41.1 openai==1.63.0 python-dotenv==1.0.1

# This tells Docker to listen on port 80 at runtime. Port 80 is the standard port for HTTP.
EXPOSE 8501

# This command creates a .streamlit directory in the home directory of the container.
RUN mkdir ~/.streamlit

# This copies your Streamlit configuration file into the .streamlit directory you just created.
RUN cp config.toml ~/.streamlit/config.toml

# Similar to the previous step, this copies your Streamlit credentials file into the .streamlit directory.
RUN cp credentials.toml ~/.streamlit/credentials.toml

ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV PYTHONUNBUFFERED=1

# This command tells Streamlit to run your app.py script when the container starts.
CMD ["streamlit", "run", "app.py"]

# CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]