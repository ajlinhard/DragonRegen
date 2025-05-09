# Project Overview
The project is about creating a data generator in pyspark which can be used to create new data sets of random data or mimic an existing data sets structure. The generators will need to handle data cardinality, uniqueness, cardinality, data type, categorical nature, and more. Data will eventually read and write to tools like Kafka, Cassandra, DynamoDB and more.


## Nexts Steps:
0) teirs to the medillion reading a airflow prediction
1) Builder structure for generating the data
    a. implement numpy data
2) Work on the FirstName and LastName detectors. 
3) Load a name files into SQL Spark and then reference it in a follow-up query.
4) Add logging, trace, and speed tracking
5) System-wide spark instance for easier appending, relationships and collaboration
6) Think through multi-column relationships? How will the talk (maybe via a builder class?)
7) Look at Microsoft token detector (Presidio) for more
8) Routing Data Table Concepts (backend mysql or postgreSQL db)
9) Profile Categorical (column_values, column_value_ratio)

- Abstract Read and Write (based of repository concept)
- Work on other column generators like catergorical, UID, First/Last name
- Create pytesting and package
    - test for data types and count
    - do speed testing.
- Add logging both to file and database
- Add better error handling
- implement NumPy version of random generator functions (compare speed test)
    - look into batch or futures for parallel generations.

## Ideas
Col Generators:
- Categorical (using Enum)
- Unique IDs (using UUID or other feature)
- Cardinality 

Data Generators:
The data generators could all be staticmethods in a class?



## Ideas (higher effort):
Global Spark Session
- Do I need to make a class level spark session? for example, StringFirstName.py needs the first name data loaded for use.
    - Maybe a singleton spark class, or a spark generator builder structure in the DataSet class?
    - Or maybe the First Name data needs to be stored in memory or accessible in spark instance via table?
Batching
- Eventually if the data is of a certain size I will need to create data in batches.

Unique Key Sets (aka foreign keys)
- These key sets must be shared between different tables with 100% or N% overlap with each other.

Hash or Composite Keys
- The column is a composite key using an algorithm such as MD5 to hash, or simple separator like "|" ex: "hello|world|!"

For QC these can be the description of the tools use cases
- Lighthouse (guiding data to safety)
- Sieve (filtering out bad data)
- Crucible (refining data)
- Prism (showing the true colors of your data)
- Curator (maintaining quality collections)

--- 
# Using Data Sets
--- 

```python
{"description": "Users can past description of the columns, if the want."
,"colType": "FirstName"
, "source": {
    "engine": "spark", # want generated the data spark, panda, numpy, Databricks, Cassandra
    "input_data_path": "cloud_url/database_name.schema.table_name.column_name"  # where the data should go. If using data routing feature can be an ID
    "output_data_path": "cloud_url/database_name.schema.table_name.column_name" # where the data. If using data routing feature can be an ID
    }
, "stats":{
    "unique": True, 
    "uniqueness_ratio": 1.0, # Value from 0.0 to 1.0 of roughly the percentage of unique values.
    "cardinality_ratios": {"col1": "1:N", "col2": "1:1", "col3": "N:M"},
    "null_ratio": .05 # how many null values are present in the column.
    "min": 1, 
    "max": None
    }
}

```

--- 
# Data Sets Useds
--- 
### String Columns
**First Names**
- [Social Security Aggregations](https://www.ssa.gov/oact/babynames/limits.html)

**Last Names/Surnames**
- [Census Bureau Aggregations](https://www.census.gov/topics/population/genealogy/data/2010_surnames.html)


--- 
# Desing Notes:
--- 
## Data Generation
When efficiently generating random data the ask can be difficult to do efficiently. Generating row-wise vs column-wise (vectorized) data can allow for optimizations.
Options Considered:
1. Python List + random package 
    Hypothesis: Simple approach with built-in common package. Could use futures to parallelize the CPU bound task.
2. NumPy random generation
    Hypothesis: NumPy is written and optimized in C, therefore it may be very fast.
3. Spark UDFs
    Hypothesis: Spark can be parallelized to may workers and servers. So, in a hardware positive (many CPUs + RAM) this method could win.

### Option 1:
With future this method can be very fast and efficient.
```python
import random
import string
import concurrent.futures
import numpy as np
from functools import partial

# Method 1: Using concurrent.futures for parallelization
def generate_random_string(min_length, max_length, charset=None):
    if charset is None:
        charset = string.ascii_letters + string.digits
    
    length = random.randint(min_length, max_length)
    return ''.join(random.choice(charset) for _ in range(length))

def generate_multiple_strings_parallel(count, min_length, max_length, charset=None):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Create a partial function with fixed parameters
        func = partial(generate_random_string, min_length, max_length, charset)
        # Execute the function 'count' times in parallel
        return list(executor.map(lambda _: func(), range(count)))
```

### Option 2:
Numpy is fast and optimized. Plus the same futures concept could work if we divide the count of data to be generated by CPU count.
```python

# Method 2: Using NumPy for vectorized operations (fastest for large counts)
def generate_multiple_strings_numpy(count, min_length, max_length, charset=None):
    if charset is None:
        charset = string.ascii_letters + string.digits
    
    # Generate random lengths for each string
    lengths = np.random.randint(min_length, max_length + 1, count)
    
    # Create a list to hold all strings
    result = []
    
    # For each desired length, generate a string of that length
    for length in lengths:
        # Generate indices into the charset
        char_indices = np.random.randint(0, len(charset), size=length)
        # Convert indices to characters and join
        random_str = ''.join(charset[i] for i in char_indices)
        result.append(random_str)
        
    return result
```

### Option 3:
Using a Spark UDF (User-Defined Function) for random string generation has both advantages and disadvantages compared to generating strings in Python and then converting to a Spark column.

In most cases, a Spark UDF for this particular task will likely be slower than the native Python approach for several reasons:

```python
import random
import string
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

# Define the UDF for random string generation
@udf(returnType=StringType())
def random_string_udf(min_length, max_length):
    length = random.randint(min_length, max_length)
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Usage in a Spark DataFrame
# df = df.withColumn("random_str", random_string_udf(lit(5), lit(15)))
```

Here's why this is generally less efficient than the Python-first approach:

1. **Serialization Overhead**: Spark UDFs require serialization/deserialization between the JVM and Python interpreter, which adds significant overhead.

2. **Row-by-Row Processing**: Spark UDFs typically process data row-by-row rather than in vectorized batches, making them inefficient for operations that could be vectorized.

3. **Poor Parallelism Management**: While Spark excels at distributed data processing, the parallelism within a UDF is not optimally managed for CPU-bound tasks like random string generation.

For better performance, consider:

1. **Generate in Python, then convert to Spark**: Generate all strings using NumPy or parallel Python methods, then create a Spark DataFrame from that collection.

2. **Use Scala UDFs**: If you must use Spark UDFs, writing them in Scala eliminates the Python-JVM serialization overhead.

3. **Use Spark's built-in functions when possible**: For related operations, Spark has optimized functions like `rand()` that are much faster than UDFs.

The most efficient approach depends on your specific workflow and data size, but for pure random string generation, Python's native capabilities (especially using NumPy vectorization) will typically outperform Spark UDFs.