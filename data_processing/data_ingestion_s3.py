import os
import json
import boto3
from datasets import load_dataset

# --- Configuration ---
BUCKET_NAME = 'chatbot-data-20596371' 
DATASET_NAME = "PaDaS-Lab/webfaq"
CONFIG_NAME = "eng"  # Fetch English subset only
REGION_NAME = "us-east-1"
BATCH_SIZE = 25000  
TOTAL_RECORDS = 20000000 

def upload_to_s3(file_name, bucket, object_name=None):
    """Uploads a local file to an AWS S3 bucket."""
    s3_client = boto3.client('s3', region_name=REGION_NAME)
    try:
        s3_client.upload_file(file_name, bucket, object_name or file_name)
        print(f"Successfully uploaded {file_name} to {bucket}")
    except Exception as e:
        print(f" Upload failed: {e}")

def main():
    print("Starting the Data Harvest Mission (20 Million Records)...")
    
    # 1. Load dataset using streaming mode to save RAM
    try:
        dataset = load_dataset(DATASET_NAME, CONFIG_NAME, split='default', streaming=True)
    except Exception as e:
        # Fallback if split='default' is not explicitly required
        dataset = load_dataset(DATASET_NAME, CONFIG_NAME, streaming=True)

    batch_data = []
    batch_count = 0
    record_count = 0

    # 2. Process records and partition into JSONL files
    for entry in dataset:
        batch_data.append(entry)
        record_count += 1

        # Check if batch size is reached
        if len(batch_data) == BATCH_SIZE:
            file_name = f"faq_batch_{batch_count}.jsonl"
            
            # Save batch locally as JSONL
            with open(file_name, 'w', encoding='utf-8') as f:
                for record in batch_data:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            # Upload the JSONL file to S3 'raw/' prefix
            s3_path = f"raw/{file_name}"
            upload_to_s3(file_name, BUCKET_NAME, s3_path)
            
            # Remove local file to save disk space
            os.remove(file_name) 
            batch_data = []
            batch_count += 1
            
            print(f"Progress: {record_count} records processed | Batch: {batch_count}")

        # Stop once the target record count is reached
        if record_count >= TOTAL_RECORDS:
            break

    print(f" Mission Accomplished! Total records uploaded to S3: {record_count}")

if __name__ == "__main__":
    main()