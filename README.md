# DragonFlow
Creating a real-time data streamering application.

## Sources:
Used this project as a base concept: https://www.youtube.com/watch?v=GqAcTrqKcrY

# Setup Steps
1. Setup Environment YAML for anaconda, instead of using venv. The file is scene in KafkaDragon.yml in the project root.
    a. For all latest package installs. The project was run on 2025-02-18.
2. Setting up an Airflow DAG.

## Notes:
Cassandra Access through docker:
    docker exec -it cassandra cqlsh -u cassandra -p cassandra localhost 9042
    -> cassandra after "-it" is the container name
    -> cassandra is located on the localhost 9042
    Example Calls:
        - describe spark_streams.created_users;
        - select * from spark_streams.created_users;

## Outstanding Questions:
    1. How does the spark queue work? EX: spark-submit --master spark://localhost:7077 spark_stream.py
        a. Could I include this submit into the Airflow DAG created for the project?
    2. How can kafka be configured to run across multiple containers or servers?

# Run Book_API with docker
1. Download the container from docker hub
2. Run with docker command
```bash
docker run -p 5000:5000 ajlinhard/book-api
```
3. Run a test curl command
```bash
Test with curl http://localhost:5000/books
```

Common issues:
- Using the FLASK_APP environment variable to set the path does not work with how the project is setup. The inheritance is setup from that execution point.
- The app must be full exposed in docker by using the commmand in number 2, plus when running the flask run method: 
```python
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

# API Section of Project
## Adds to requirements.txt
```
flask
flask-restful
flask-cors
```
## Project Structure Explanation

1. **Models** (models/book.py)
   - Define data structures
   - Provide basic data validation and conversion

2. **Services** (services/book_service.py)
   - Handle business logic
   - Manage data operations
   - In a real app, this would interact with a database

3. **Resources** (resources/book_resource.py)
   - Define API endpoints
   - Handle HTTP request/response
   - Use services to perform operations

4. **App Configuration** (app.py)
   - Create Flask application
   - Set up routes
   - Configure middleware

## Benefits of This Approach
- Modular and organized code
- Separation of concerns
- Easy to maintain and extend
- Simple to add new resources
- Testability improved

## Recommendations for Production
- Replace in-memory storage with a database
- Add proper error handling
- Implement authentication
- Use environment configuration
- Add logging
```

This modular approach provides a clean, organized structure for a Python API. Let me break down the key aspects:

1. **Separation of Concerns**
   - `models/` defines data structures
   - `services/` handles business logic
   - `resources/` manages API endpoints
   - `app.py` sets up the application

2. **Flexibility**
   - Easy to add new endpoints
   - Simple to swap out services (e.g., switch from in-memory to database)
   - Clean, maintainable code structure

3. **Scalability**
   - Each component has a specific responsibility
   - Can easily add more complex logic in services
   - Supports future expansion

To run this API:
1. Set up a virtual environment
2. Install requirements: `pip install -r requirements.txt`
3. Run the app: `python app.py`
