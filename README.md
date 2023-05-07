# About
This is a project for practicing Cloud development.
We implement a simple Flask server for creating and getting Dishes and Meals

# Usage instructions
## Prerequisits
* Have Docker installed

## Running the server
* Use the Dockerfile to create an image, e.g. `docker build -t flask .`
* Use `docker run --rm -p 8000:8000 flask` to run a container

## Using the server
* You can see the test.py with a usage example with some tests

## Running the server with a different port
* Build with specifying the port: `docker build -t flask .  --build-arg port=3000`
* Run with specified port: `docker run --rm -p 8000:3000 flask`
