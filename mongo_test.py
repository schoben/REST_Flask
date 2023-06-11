from pymongo import MongoClient


# Connect to MongoDB
client = MongoClient('localhost', 27017)

# Access a specific database
db = client['mydatabase']

# Access a specific collection
collection = db['mycollection']

# Insert a document
document = {'name': 'John Doe', 'age': 30}
insert_result = collection.insert_one(document)
print('Inserted document ID:', insert_result.inserted_id)

# Find documents
query = {'name': 'John Doe'}
results = collection.find(query)
for result in results:
    print(result)

# Update a document
query = {'name': 'John Doe'}
new_values = {'$set': {'age': 35}}
update_result = collection.update_one(query, new_values)
print('Modified document count:', update_result.modified_count)

# Delete a document
query = {'name': 'John Doe'}
delete_result = collection.delete_one(query)
print('Deleted document count:', delete_result.deleted_count)

# Disconnect from MongoDB
client.close()

