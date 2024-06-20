from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for
import os
import pymongo
import redis

# Create a Flask app instance
app = Flask(__name__)

# Configure Redis connection
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_connection = redis.from_url(redis_url)

# Configure MongoDB connection
mongo_url = os.getenv("MONGO_URL", "mongodb://root:root@localhost:27017")
mongo_client = pymongo.MongoClient(mongo_url)
mongo_db = mongo_client["TaskManagerDB"]
mongo_collection = mongo_db["Tasks"]

# Define the index route
@app.route('/')
def index():
    ip = request.remote_addr  # Get the user's IP address from the request

    # Retrieve the user's tasks directly from MongoDB
    todo_list = mongo_collection.find({'ip': ip})

    # Render the HTML template with the task list
    return render_template('index.html', todo_list=todo_list)

# Define the add route for adding tasks
@app.route('/add', methods=['POST'])
def add():
    ip = request.remote_addr    # Get the user's IP address from the request
    task = request.form.get('task')  # Get the task text from the form

    # Check if a valid task is provided
    if task:
        # Insert the task into MongoDB with the user's IP address
        mongo_collection.insert_one({'task': task, "ip": ip})

    # Redirect back to the index page
    return redirect(url_for('index'))

# Define the delete route for deleting tasks
@app.route('/delete/<task_id>')
def delete(task_id):
    try:
        task_id = ObjectId(task_id)  # Convert the task_id to a MongoDB ObjectId
    except Exception as e:
        print("Invalid task_id:", e)

    # Attempt to delete the task from MongoDB
    result = mongo_collection.delete_one({'_id': task_id})

    # Check if the task was deleted successfully
    if result.deleted_count == 1:
        print("Task deleted successfully.")
    else:
        print("Task not found or an error occurred.")

    # Redirect back to the index page
    return redirect(url_for('index'))

# Start the Flask app if this script is run directly
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
