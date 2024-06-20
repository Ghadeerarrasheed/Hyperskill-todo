# Dockerized ToDo application for Hyper Skill article
## Building and Deploying a Flask To-Do App with Docker, MongoDB, and Redis

In this article, we will guide you through creating a simple To-Do application using Flask, MongoDB, and Redis. We will then Dockerize the application to make it easy to deploy and run consistently across different environments. Let's dive in!

Prerequisites

 * Docker installed on your system
 * Basic knowledge of Python and Flask
 * Basic understanding of Docker and Docker Compose

### Project Structure

Here’s the project structure we will follow:

```
todo-app/
│
├── app/
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   └── style.css
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
└── docker-compose.yml
```


#### Step 1: Setting Up the Flask Application

First, create the Flask application.

``app/app.py:``

```python
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
```

app/templates/index.html:

```html
<!DOCTYPE html>
<html>
<head>
    <title>To-Do List</title>
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
</head>
<body>
    <div class="container">
        <h1>To-Do List</h1>
        <form class="add-task-form" method="POST" action="/add">
            <input type="text" name="task" placeholder="Add a new task" required>
            <button type="submit">Add</button>
        </form>
        <ul class="todo-list">
            {% for task in todo_list %}
                <li>
                    {{ task.task }}
                    <a href="/delete/{{ task._id }}" class="delete-task"><i class="fa fa-trash" aria-hidden="true"></i></a>
                </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
```

app/static/style.css:

```css
body, h1, ul {
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
    display: flex; /* Add this line */
    justify-content: center; /* Add this line */
    align-items: center; /* Add this line */
    height: 100vh; /* Add this line */
}

.container {
    max-width: 400px;
    margin: 0 auto; /* Center the container horizontally */
    padding: 70px;
    background-color: #ffffff;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

h1 {
    text-align: center;
    margin-bottom: 20px;
    color: #333;
}

.add-task-form {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
}

.add-task-form input[type="text"] {
    flex-grow: 1;
    padding: 8px;
    border: none;
    border-radius: 3px;
    font-size: 16px;
}

.add-task-form button {
    background-color: #007bff;
    color: #fff;
    border: none;
    border-radius: 3px;
    padding: 8px 15px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.2s;
}

.add-task-form button:hover {
    background-color: #0056b3;
}

.todo-list {
    list-style-type: none;
    padding: 0;
    margin-top: 20px;
}

.todo-list li {
    background-color: #ffffff;
    border: 1px solid #ddd;
    margin-bottom: 10px;
    padding: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 3px;
    transition: box-shadow 0.2s;
}

.todo-list li:hover {
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
}

.delete-task {
    text-decoration: none;
    color: #ff0000;
    margin-left: 10px;
    padding: 2px 5px;
    border: 1px solid #ff0000;
    border-radius: 3px;
}

.delete-task:hover {
    background-color: #ff0000;
    color: #fff;
}
```

app/requirements.txt:

```
Flask==2.0.2
redis==3.5.3
pymongo==3.12.0
```

#### Step 2: Create the Dockerfile

app/Dockerfile:

```Dockerfile
FROM python:3.9.7-alpine3.14

ENV TODO /todo-list
WORKDIR $TODO

COPY . . 

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
```

#### Step 3: Create the Docker Compose Configuration

docker-compose.yml:

```yaml
version: "3"
services:
  webapp:
    build: ./app
    container_name: "webapp"
    ports:
      - "8080:8080"
    environment:
      REDIS_URL: redis://redis:6379
      MONGO_URL: mongodb://root:root@mongo:27017
    depends_on:
      - redis
      - mongo    
  redis:
    image: "redis:6.2.6-buster"
    ports:
      - "6379:6379"
  mongo:
    image: "mongo:4.4-rc-focal"
    ports:
      - "27017:27017"
```

#### Step 4: Building and Running the Docker Containers

Now that we have everything set up, let's build and run our Docker containers.

1. Navigate to the project root directory (`todo-app`) and build the Docker images:

   ```sh
   docker-compose build
   ```

2. Start the Docker containers:

   ```sh
   docker-compose up
   ```
This command will build the Docker images for your Flask app, MongoDB, and Redis, and start the containers. You should see output indicating that each service is starting.

3. Access the Flask application:

   Open your browser and navigate to `http://localhost:8080`. You should see the To-Do application interface.

Docker Commands Overview

Here are some basic Docker commands you might find useful:

- **Build Docker images:**

  ```sh
  docker-compose build
  ```

- **Start Docker containers:**

  ```sh
  docker-compose up
  ```

- **Stop Docker containers:**

  ```sh
  docker-compose down
#### Step 5: Building and Pushing the Docker Image to Docker Hub

After creating your Dockerfile and docker-compose.yml, the next step is to build the Docker image and push it to your Docker Hub registry. Follow these steps:

1. Log in to Docker Hub:

   First, make sure you are logged in to your Docker Hub account. If you don't have an account, you can create one at [Docker Hub](https://hub.docker.com/).

   ```sh
   docker login
   ```

   You will be prompted to enter your Docker Hub username and password.

2. Build the Docker Image:

   Navigate to the directory containing your Dockerfile (`app` directory) and build the Docker image. Replace `ghadeer99/todo-app` with your Docker Hub username and desired repository name.

   ```sh
   docker build -t ghadeer99/todo-app:latest .
   ```

3. Tag the Docker Image:

   Tag your Docker image for versioning. This step is optional but recommended for better management of your images.

   ```sh
   docker tag ghadeer99/todo-app:latest ghadeer99/todo-app:v1.0
   ```

4. Push the Docker Image to Docker Hub:

   Push the Docker image to your Docker Hub repository.

   ```sh
   docker push ghadeer99/todo-app:latest
   ```

   If you tagged your image, push the tagged version as well:

   ```sh
   docker push ghadeer99/todo-app:v1.0
   ```

Full Dockerfile and Docker Compose Workflow

Here's a full walkthrough of building, tagging, and pushing your Docker image:

1. Build the Docker Image:

   ```sh
   cd app
   docker build -t ghadeer99/todo-app:latest .
   ```

2. Tag the Docker Image:

   ```sh
   docker tag ghadeer99/todo-app:latest ghadeer99/todo-app:v1.0
   ```

3. Log in to Docker Hub:

   ```sh
   docker login
   ```

4. Push the Docker Image:

   ```sh
   docker push ghadeer99/todo-app:latest
   docker push ghadeer99/todo-app:v1.0
   ```

Final Docker Compose Configuration

Make sure your `docker-compose.yml` is configured to use the image you pushed to Docker Hub:

docker-compose.yml:

```yaml
version: "3"
services:
  webapp:
    image: "ghadeer99/todo-app:latest"
    container_name: "webapp"
    ports:
      - "8080:8080"
    environment:
      REDIS_URL: redis://redis:6379
      MONGO_URL: mongodb://root:root@mongo:27017
    depends_on:
      - redis
      - mongo    
  redis:
    image: "redis:6.2.6-buster"
    ports:
      - "6379:6379"
  mongo:
    image: "mongo:4.4-rc-focal"
    ports:
      - "27017:27017"
```

Running the Docker Compose

Now you can run your application using Docker Compose with the image from Docker Hub:

```sh
docker-compose up
```

This command will pull the image from Docker Hub and start the containers.

Conclusion

You've now successfully created, Dockerized, and pushed a Flask To-Do application to Docker Hub. This allows you to deploy your application easily across different environments. You can further enhance this setup by adding CI/CD pipelines to automate the build and push process.

Happy coding!


