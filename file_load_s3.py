import json
import boto3
import pandas as pd
import urllib.parse
from datetime import datetime
import io

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
        
        # Assume the file is a CSV and read it into a pandas DataFrame
        # io.BytesIO creates a binary stream in memory
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Add a new column with the current timestamp
        df['ProcessedTime'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save the modified DataFrame to a new file in S3
        output_key = f"processed/{key.split('/')[-1]}"  # Save to 'processed/' prefix
        
		#Creates an in-memory text buffer for writing CSV outpu
        output_buffer = io.StringIO()
        df.to_csv(output_buffer, index=False)
        
        s3_client.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=output_buffer.getvalue().encode()
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully processed {key} and saved to {output_key}")
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing {key}: {str(e)}")
        }