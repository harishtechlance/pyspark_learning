# PySpark Learning - Getting Started

## 1. Create Spark Session


```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Learning PySpark") \
    .getOrCreate()

print(f"Spark Version: {spark.version}")
```

## 2. Create Sample Data


```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Define schema
schema = StructType([
    StructField("City", StringType(), True),
    StructField("State", StringType(), True),
    StructField("Population", IntegerType(), True)
])

# Create data
data = [
    ("New York", "NY", 8000000),
    ("Los Angeles", "CA", 3900000),
    ("Chicago", "IL", 2700000),
    ("Houston", "TX", 2300000),
    ("Phoenix", "AZ", 1600000)
]

# Create DataFrame
df = spark.createDataFrame(data, schema=schema)
df.show()
```

## 3. Basic Operations


```python
# Show schema
df.printSchema()

# Count rows
print(f"Total cities: {df.count()}")

# Select specific columns
df.select("City", "Population").show()

# Filter data
df.filter(df.Population > 3000000).show()
```

## 4. Transformations


```python
from pyspark.sql.functions import col, upper, round as spark_round

# Add new column
df_new = df.withColumn("City_Upper", upper(col("City")))

# Calculate density (simplified)
df_new = df_new.withColumn("PopDensity", spark_round(col("Population") / 100, 2))

df_new.show()
```

## 5. Aggregations


```python
# Group by and aggregate
result = df.groupBy("State").agg({
    "Population": "sum",
    "City": "count"
}).withColumnRenamed("sum(Population)", "Total_Population") \
 .withColumnRenamed("count(City)", "Num_Cities")

result.show()
```

## 6. Read CSV


```python
# Place your CSV in the data folder first
csv_path = "/home/jovyan/data/sample.csv"

# Read CSV
df_csv = spark.read.option("header", "true").option("inferSchema", "true").csv(csv_path)
df_csv.show()
```

## 7. Write to PostgreSQL


```python
# Save to PostgreSQL
df.write \
    .format("jdbc") \
    .mode("overwrite") \
    .option("url", "jdbc:postgresql://postgres:5432/pyspark_db") \
    .option("dbtable", "cities") \
    .option("user", "pyspark_user") \
    .option("password", "pyspark_pass") \
    .option("driver", "org.postgresql.Driver") \
    .save()

print("Data written to PostgreSQL!")
```

## Next Steps

1. Try more transformations (join, window functions, etc.)
2. Load real CSV data from the `data/` folder
3. Practice SQL queries on DataFrames
4. Learn about performance tuning and caching
