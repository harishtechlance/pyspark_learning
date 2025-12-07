"""
Sample PySpark job for learning
Reads CSV from local data folder and performs transformations
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, upper, when
import os

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("PySpark Learning") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.memory", "2g") \
    .config("spark.executor.cores", "2") \
    .getOrCreate()

# Set log level to WARN to reduce output
spark.sparkContext.setLogLevel("WARN")

def load_csv(file_path):
    """Load CSV file into DataFrame"""
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(file_path)
    return df

def transform_data(df):
    """Perform transformations on the data"""
    # Convert city to uppercase
    df_transformed = df.withColumn("City", upper(col("City")))
    
    # Add a new column for Census category
    df_transformed = df_transformed.withColumn(
        "Census_Category",
        when(col("Census_2020") > 500000, "Large City")
        .when(col("Census_2020") > 100000, "Medium City")
        .otherwise("Small City")
    )
    
    return df_transformed

def save_to_postgres(df, mode="overwrite"):
    """Save DataFrame to PostgreSQL"""
    try:
        df.write \
            .format("jdbc") \
            .mode(mode) \
            .option("url", "jdbc:postgresql://postgres:5432/pyspark_db") \
            .option("dbtable", "cities_data") \
            .option("user", "pyspark_user") \
            .option("password", "pyspark_pass") \
            .option("driver", "org.postgresql.Driver") \
            .save()
        print("Successfully saved to PostgreSQL")
    except Exception as e:
        print(f"Error saving to PostgreSQL: {e}")

def main():
    """Main function"""
    data_path = "/opt/spark/data/sample_data.csv"
    
    # Check if file exists
    if not os.path.exists(data_path):
        print(f"File not found at {data_path}")
        print("Please add sample_data.csv to the data folder")
        return
    
    # Load data
    print("Loading data...")
    df = load_csv(data_path)
    df.show()
    
    # Transform data
    print("\nTransforming data...")
    df_transformed = transform_data(df)
    df_transformed.show()
    
    # Save to PostgreSQL
    print("\nSaving to PostgreSQL...")
    save_to_postgres(df_transformed)
    
    spark.stop()

if __name__ == "__main__":
    main()
