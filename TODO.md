What to do next?


* Change the ID and NAME resources of the dish collection to use mongo
* Convert meals to use mongo DB
* Implement the diets resource (in a separate module, e.g. diets.py)
* Create a Dockerfile for the diets service
* Update the meals service to communicate with the Diets service
* Add nginx to the Docker-compose
* Add building of the Dockerfiles to the docker-compose


Also need:
* Way to reset the mongo DB
* Fix mistakes from ex1
* Verify that it is possible to 'connect' to the containers so they can be killed (in testing)
* Go over TODO statements and remove whatever we can
* write some test




### FROM EX1

# Major
* Deal with deletion of a dish that is already a part of a meal
* Test for a dish with impossible name
* Write a Dockerfile to wrap the server
    - Make port configurable
* How do we pass the API-Ninja API Key to the docker?

# Minor
* Deal with request headers
* Use integer for the endpoint when using ID
* Deal with badly formatted JSON input (See slide 14)
* Deal with non-JSON input


# Extra
* Pytest
* Separate to different modules (separate 'data' classes from REST implementation)
* Uniformity with _ prefix
* Type hints
* Remove any 'TODO'
* Removed unnecessary comments

# Questions
* Indexing of dishes. Can we reuse the same index?
* Am I using the 'subresources' correctly?

