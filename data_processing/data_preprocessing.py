from pyspark.sql import SparkSession

# Step 1: Initialize Spark Session
# Creating a Spark session configured for the preprocessing job on the EMR cluster.
spark = SparkSession.builder \
    .appName("Chatbot_Preprocessing_Hanaa_Sampled") \
    .getOrCreate()

# Step 2: Define S3 Input and Output Paths
# Utilizing the S3 bucket to read raw JSONL files and store the processed Parquet files.
bucket_name = "chatbot-data-20596371"
input_path = f"s3://{bucket_name}/raw/faq_batch_*.jsonl" 
output_path = f"s3://{bucket_name}/processed_data/"

# Step 3: Data Ingestion
# Reading all raw JSONL files from the specified S3 directory into a Spark DataFrame.
print("Step 1: Reading all JSONL files from raw folder...")
df = spark.read.json(input_path)

# Step 4: Stratified Sampling (Resource Optimization)
# Due to hardware constraints (m4.large limits) and a massive 20M record dataset, 
# a 5% sample (approx. 1 Million records) is extracted. 
# seed=42 ensures reproducibility across multiple runs.
print("Step 2: Sampling 5% of the data...")
df_sampled = df.sample(withReplacement=False, fraction=0.05, seed=42)

# Step 5: Data Cleaning
# Removing any rows containing null values to ensure high data quality for fine-tuning.
print("Step 3: Cleaning data (dropping nulls)...")
df_final = df_sampled.dropna()

# Step 6: Data Persistence and Format Transformation
# Writing the cleaned, sampled dataset back to S3 in Parquet format.
# Parquet is chosen because its columnar storage reduces size and speeds up subsequent ML tasks.
print(f"Step 4: Writing the sampled data to {output_path} in Parquet format...")
df_final.write.mode("overwrite").parquet(output_path)

print("SUCCESS: The Spark job finished successfully!")
spark.stop()