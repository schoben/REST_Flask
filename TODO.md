What to do next?


Also need:
* Make sure return values are the same as specified in the assignment
* Fix mistakes from ex1
* Verify that it is possible to 'connect' to the containers so they can be killed (in testing)
* Go over TODO statements and remove whatever we can
* write some test for diets + meals combo





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

