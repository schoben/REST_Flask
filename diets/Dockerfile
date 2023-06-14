FROM python:alpine3.17

# Setting an Environment variable for the API key
# We supply a default API Key, while allowing other keys to be used
ARG KEY=GZhBLJkOriPZwhCOJlOdHg==UEeUzdzoKypBxfto
ENV NINJA_API_KEY=$KEY
ENV FLASK_APP=diets.py

# Setting the application & requirements
COPY requirements.txt diets.py app/
WORKDIR ./app
RUN pip install -r requirements.txt

# Set port for the server. Default is 8000, but can be changed
ARG port=5002
ENV FLASK_RUN_PORT=$port
EXPOSE $port

# Run the server
CMD ["flask", "run", "--host=0.0.0.0"]
