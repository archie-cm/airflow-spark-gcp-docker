import sys
from pyspark.sql import SparkSession, functions
from pyspark.sql.types import StringType
from modules import moduleExample
import pandas as pd
import pandas_gbq
import os 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/opt/airflow/service-account.json"

# Create spark session
spark = (SparkSession
    .builder
    .getOrCreate()
)
sc = spark.sparkContext
sc.setLogLevel("WARN")

####################################
# Parameters
####################################
csv_file = sys.argv[1]

####################################
# Read CSV Data
####################################
print("######################################")
print("READING CSV FILE")
print("######################################")

df_csv = (
    spark.read
    .format("csv")
    .option("header", True)
    .load(csv_file)
)

print("######################################")
print("SAMPLING CSV DATA")

# Applying the Spark function
df_csv_sample = moduleExample.pysparkFunctions.sample_df(df_csv, 0.1)

print("Number of rows after sampling: {}".format(df_csv_sample.count())) 
print("######################################")

print("######################################")
print("ASSIGNING UUID")
print("######################################")

# Applying the python function. We don't need to create UDF in spark since spark version 3.1
df_csv_sample = df_csv_sample.withColumn("uuid", moduleExample.pythonFunctions.generate_uuid())

print("######################################")
print("PRINTING 10 ROWS OF SAMPLE DF")
print("######################################")

df_csv_sample.show(10)

df_csv_pandas = df_csv.toPandas()

# TODO: Set project_id to your Google Cloud Platform project ID.
project_id = "data-fellowship-9-project"

# TODO: Set dataset_id to the full destination dataset ID.
table_id = 'staging.hello-world'

pandas_gbq.to_gbq(df_csv_pandas, table_id, project_id=project_id)

