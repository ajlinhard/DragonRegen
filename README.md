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