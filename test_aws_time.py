# test_aws_time.py
import boto3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print(f"Current system time: {datetime.now()}")

try:
    client = boto3.client(
        'ses',
        aws_access_key_id=process.env("aws_access_key_id"),
        aws_secret_access_key= process.env('aws_secret_access_key'),
        region_name=process.env('region_name')
    )
    
    response = client.get_send_quota()
    print("✅ AWS credentials work!")
    print(f"   Send quota: {response['Max24HourSend']}")
    
except Exception as e:
    print(f"❌ AWS error: {e}")