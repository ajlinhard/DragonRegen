from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, DateType, TimestampType, BooleanType, ArrayType
import random
import string
from datetime import datetime, timedelta
import uuid

def create_spark_session(app_name="DummyDataGenerator"):
    """Create a Spark session."""
    return SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()

def generate_random_string(length=10):
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_random_date(start_date=datetime(2020, 1, 1), end_date=datetime(2023, 12, 31)):
    """Generate a random date between start_date and end_date."""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def generate_customer_data(spark, num_rows=1000):
    """Generate dummy customer data."""
    data = []
    
    for i in range(num_rows):
        customer_id = str(uuid.uuid4())
        name = generate_random_string(15)
        age = random.randint(18, 80)
        email = f"{name.lower()}@example.com"
        signup_date = generate_random_date()
        is_active = random.choice([True, False])
        num_purchases = random.randint(0, 100)
        
        data.append((customer_id, name, age, email, signup_date.date(), is_active, num_purchases))
    
    schema = StructType([
        StructField("customer_id", StringType(), False),
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), True),
        StructField("email", StringType(), True),
        StructField("signup_date", DateType(), True),
        StructField("is_active", BooleanType(), True),
        StructField("num_purchases", IntegerType(), True)
    ])
    
    return spark.createDataFrame(data, schema)

def generate_transaction_data(spark, num_rows=5000, customer_ids=None):
    """Generate dummy transaction data."""
    if customer_ids is None:
        # Generate random customer IDs if not provided
        customer_ids = [str(uuid.uuid4()) for _ in range(100)]
    
    data = []
    
    for i in range(num_rows):
        transaction_id = str(uuid.uuid4())
        customer_id = random.choice(customer_ids)
        transaction_date = generate_random_date()
        amount = round(random.uniform(10.0, 1000.0), 2)
        product_id = f"PROD-{random.randint(1000, 9999)}"
        quantity = random.randint(1, 10)
        
        data.append((transaction_id, customer_id, transaction_date.date(), amount, product_id, quantity))
    
    schema = StructType([
        StructField("transaction_id", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("transaction_date", DateType(), True),
        StructField("amount", FloatType(), True),
        StructField("product_id", StringType(), True),
        StructField("quantity", IntegerType(), True)
    ])
    
    return spark.createDataFrame(data, schema)

def generate_product_data(spark, num_rows=100):
    """Generate dummy product data."""
    data = []
    
    categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Food", "Toys"]
    
    for i in range(num_rows):
        product_id = f"PROD-{random.randint(1000, 9999)}"
        name = f"Product-{generate_random_string(8)}"
        category = random.choice(categories)
        price = round(random.uniform(5.0, 500.0), 2)
        stock = random.randint(0, 1000)
        rating = round(random.uniform(1.0, 5.0), 1)
        is_available = random.choice([True, False])
        
        data.append((product_id, name, category, price, stock, rating, is_available))
    
    schema = StructType([
        StructField("product_id", StringType(), False),
        StructField("name", StringType(), True),
        StructField("category", StringType(), True),
        StructField("price", FloatType(), True),
        StructField("stock", IntegerType(), True),
        StructField("rating", FloatType(), True),
        StructField("is_available", BooleanType(), True)
    ])
    
    return spark.createDataFrame(data, schema)

def generate_web_log_data(spark, num_rows=10000):
    """Generate dummy web log data."""
    data = []
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (Linux; Android 10; SM-A505F) AppleWebKit/537.36"
    ]
    
    pages = ["/home", "/products", "/cart", "/checkout", "/account", "/about", "/contact"]
    
    methods = ["GET", "POST", "PUT", "DELETE"]
    
    status_codes = [200, 201, 204, 400, 401, 403, 404, 500]
    
    for i in range(num_rows):
        log_id = str(uuid.uuid4())
        ip_address = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        user_agent = random.choice(user_agents)
        timestamp = generate_random_date()
        page = random.choice(pages)
        method = random.choice(methods)
        status_code = random.choice(status_codes)
        response_time = round(random.uniform(0.1, 5.0), 3)
        
        data.append((log_id, ip_address, user_agent, timestamp, page, method, status_code, response_time))
    
    schema = StructType([
        StructField("log_id", StringType(), False),
        StructField("ip_address", StringType(), True),
        StructField("user_agent", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("page", StringType(), True),
        StructField("method", StringType(), True),
        StructField("status_code", IntegerType(), True),
        StructField("response_time", FloatType(), True)
    ])
    
    return spark.createDataFrame(data, schema)

def generate_nested_data(spark, num_rows=500):
    """Generate dummy data with nested structures."""
    data = []
    
    for i in range(num_rows):
        order_id = str(uuid.uuid4())
        customer_name = generate_random_string(15)
        order_date = generate_random_date()
        total_amount = round(random.uniform(50.0, 2000.0), 2)
        
        # Generate random number of items in the order
        num_items = random.randint(1, 5)
        items = []
        
        for j in range(num_items):
            item = {
                "product_id": f"PROD-{random.randint(1000, 9999)}",
                "name": f"Product-{generate_random_string(8)}",
                "price": round(random.uniform(10.0, 200.0), 2),
                "quantity": random.randint(1, 10)
            }
            items.append(item)
        
        data.append((order_id, customer_name, order_date.date(), total_amount, items))
    
    schema = StructType([
        StructField("order_id", StringType(), False),
        StructField("customer_name", StringType(), True),
        StructField("order_date", DateType(), True),
        StructField("total_amount", FloatType(), True),
        StructField("items", ArrayType(
            StructType([
                StructField("product_id", StringType(), True),
                StructField("name", StringType(), True),
                StructField("price", FloatType(), True),
                StructField("quantity", IntegerType(), True)
            ])
        ), True)
    ])
    
    return spark.createDataFrame(data, schema)

def main():
    """Main function to demonstrate data generation."""
    spark = create_spark_session()
    
    # Generate different types of dummy data
    customer_df = generate_customer_data(spark, 1000)
    print("Customer Data Schema:")
    customer_df.printSchema()
    print("Customer Data Sample:")
    customer_df.show(5)
    
    # Extract customer IDs to use in transaction data
    customer_ids = [row.customer_id for row in customer_df.select("customer_id").collect()]
    
    transaction_df = generate_transaction_data(spark, 5000, customer_ids)
    print("\nTransaction Data Schema:")
    transaction_df.printSchema()
    print("Transaction Data Sample:")
    transaction_df.show(5)
    
    product_df = generate_product_data(spark, 100)
    print("\nProduct Data Schema:")
    product_df.printSchema()
    print("Product Data Sample:")
    product_df.show(5)
    
    web_log_df = generate_web_log_data(spark, 1000)
    print("\nWeb Log Data Schema:")
    web_log_df.printSchema()
    print("Web Log Data Sample:")
    web_log_df.show(5)
    
    nested_df = generate_nested_data(spark, 500)
    print("\nNested Data Schema:")
    nested_df.printSchema()
    print("Nested Data Sample:")
    nested_df.show(5)
    
    # Save data to parquet files (optional)
    customer_df.write.mode("overwrite").parquet("customer_data.parquet")
    transaction_df.write.mode("overwrite").parquet("transaction_data.parquet")
    product_df.write.mode("overwrite").parquet("product_data.parquet")
    web_log_df.write.mode("overwrite").parquet("web_log_data.parquet")
    nested_df.write.mode("overwrite").parquet("nested_data.parquet")
    
    spark.stop()

if __name__ == "__main__":
    main()