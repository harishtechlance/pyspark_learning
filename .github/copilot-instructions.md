# PySpark Learning Environment - AI Agent Instructions

## Project Overview

This is a **Docker-based PySpark learning environment** designed for:
- Interactive PySpark development via Jupyter notebooks
- Batch job execution against a Spark cluster
- Data persistence in PostgreSQL
- Integration with Apache Airflow (running separately in `D:\Software_Projects\materials`)

**Architecture**: Local Spark cluster (master + worker) + Jupyter + PostgreSQL, all containerized via docker-compose.

## Key Services & Networking

### Service Details
- **spark-master** (port 8082): Cluster master at `spark://spark-master:7077`
- **spark-worker** (port 8081): Depends on spark-master
- **pyspark-jupyter** (port 8888): Pre-configured with PySpark support
- **pyspark-postgres** (port 5433): Credentials in docker-compose.yaml

### Important Networking
- **Container-to-container**: Use service names (e.g., `postgres:5432`, `spark-master:7077`)
- **Host access**: Use `localhost` with mapped ports (e.g., `localhost:5433`)
- **Shared network**: `pyspark-network` (bridge driver)

## Development Workflows

### Running PySpark Code

**Interactive (Jupyter)**
```python
# Jobs mounted at /opt/spark/jobs, data at /opt/spark/data
spark = SparkSession.builder \
    .appName("MyApp") \
    .master("spark://spark-master:7077") \
    .getOrCreate()
df = spark.read.csv("/opt/spark/data/myfile.csv", header=True, inferSchema=True)
```

**Batch (Command line)**
```powershell
docker exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  /opt/spark/jobs/sample_job.py
```

### Container Management
- Start: `docker-compose up -d`
- Stop: `docker-compose down`
- Clean: `docker-compose down -v` (removes volumes)
- Logs: `docker-compose logs [service-name]`

## Project-Specific Patterns

### File Structure
```
jobs/          # Python scripts for spark-submit execution
data/          # CSV/data files (mounted as /opt/spark/data)
notebooks/     # Jupyter notebooks (mounted as /home/jovyan/work)
airflow/dags/  # (Reserved for future Airflow DAG integration)
```

### PySpark Configuration Conventions
From `jobs/sample_job.py`:
- Always set `.master("spark://spark-master:7077")` for cluster submission
- Use `.config("spark.executor.memory", "2g")` (matches docker-compose limits)
- Set log level to WARN: `spark.sparkContext.setLogLevel("WARN")`

### Data I/O Patterns
- **CSV input**: Use `spark.read.option("header", "true").option("inferSchema", "true").csv(path)`
- **PostgreSQL output**: Use JDBC format with credentials from docker-compose:
  ```python
  df.write.format("jdbc") \
    .option("url", "jdbc:postgresql://postgres:5432/pyspark_db") \
    .option("user", "pyspark_user") \
    .option("password", "pyspark_pass") \
    .option("dbtable", "target_table") \
    .mode("overwrite").save()
  ```

## Critical Conventions & Gotchas

1. **Port conflicts**: Spark UI (8080) intentionally avoids Airflow (8000), Jupyter (8888), PostgreSQL (5433)
2. **No Airflow in this compose**: Airflow runs separately in materials project; create DAGs to call Spark jobs via SSH/docker exec
3. **Data persistence**: PostgreSQL volume (`postgres-data`) survives `docker-compose down` but is destroyed by `docker-compose down -v`
4. **Jupyter auth disabled**: Notebooks are open (`--NotebookApp.token='' --NotebookApp.password=''`) - local development only

## Integration with External Systems

### With Airflow (materials project)
- Airflow can trigger Spark jobs via:
  - `BashOperator` calling `docker exec spark-master spark-submit`
  - Or SSH if containers networked across projects
- Spark output should write to shared PostgreSQL instance for Airflow orchestration visibility

### External Data Sources
- Place CSV files in `data/` folder (mounted as `/opt/spark/data`)
- Reference in PySpark as `/opt/spark/data/filename.csv`
- PostgreSQL accessible from host at `localhost:5433`

## When Adding New Features

1. **New PySpark job**: Place `.py` file in `jobs/` folder, reference `spark://spark-master:7077` master URL
2. **New dependencies**: Update Jupyter image in docker-compose or use `pip install` in notebook cell
3. **New PostgreSQL table**: Create via Spark job's JDBC write or manual SQL connection
4. **Airflow integration**: Add DAG to materials project referencing this Spark cluster
