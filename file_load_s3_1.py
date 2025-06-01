#s3_client.upload_file automatically handles large files by using multipart upload for files exceeding the default threshold (8 MB). I

#Example: For a 10 GB file, upload_file splits it into ~2,000 parts (5 MB each) and uploads them concurrently, ensuring efficient and reliable transfer to S3.

#upload_file in Lambda, you must write the file to /tmp/


import json
import boto3
import pandas as pd
import urllib.parse
from datetime import datetime
import os

def lambda_handler(event, context):
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    try:
        # Extract bucket and key from the S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        
        # Get the object from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read()
        
        # Read CSV into a pandas DataFrame
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Add a new column with the current timestamp
        df['ProcessedTime'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save the modified DataFrame to a temporary file in /tmp/
        temp_file = f"/tmp/processed_{key.split('/')[-1]}"
        df.to_csv(temp_file, index=False)
        
        # Upload the temporary file to S3
        output_key = f"processed/{key.split('/')[-1]}"  # Save to 'processed/' prefix
        s3_client.upload_file(
            Filename=temp_file,
            Bucket=bucket,
            Key=output_key
        )
        
        # Clean up the temporary file
        os.remove(temp_file)
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully processed {key} and uploaded to {output_key}")
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing {key}: {str(e)}")
        }