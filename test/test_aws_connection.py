"""
Test script to verify AWS S3 and SQS connectivity and operations
"""
import json
import sys
from datetime import datetime
from aws.s3_client import get_s3_client
from aws.sqs_client import get_sqs_client
from config.settings import S3_BUCKET_NAME, SQS_QUEUE_URL, SQS_QUEUE_NAME
from utils.logger import get_logger

logger = get_logger(__name__)

def test_s3_connection():
    """Test S3 bucket access and upload capability."""
    print("\n" + "="*60)
    print("TESTING S3 CONNECTION")
    print("="*60)
    
    try:
        s3_client = get_s3_client()
        if not s3_client:
            print("❌ Failed to create S3 client")
            return False
        
        print(f"✓ S3 client created successfully")
        print(f"  Bucket: {S3_BUCKET_NAME}")
        
        # Test 1: Check if bucket exists
        print("\n1. Checking bucket access...")
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            print(f"   ✓ Bucket '{S3_BUCKET_NAME}' is accessible")
        except Exception as e:
            print(f"   ❌ Cannot access bucket: {str(e)}")
            return False
        
        # Test 2: Upload a test file
        print("\n2. Testing file upload...")
        test_key = f"test/connection_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_content = f"AWS Connection Test - {datetime.now().isoformat()}"
        
        try:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain'
            )
            print(f"   ✓ Successfully uploaded test file to: {test_key}")
        except Exception as e:
            print(f"   ❌ Upload failed: {str(e)}")
            return False
        
        # Test 3: Read the file back
        print("\n3. Testing file download...")
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=test_key)
            content = response['Body'].read().decode('utf-8')
            if content == test_content:
                print(f"   ✓ Successfully downloaded and verified file")
            else:
                print(f"   ⚠ Downloaded content doesn't match")
        except Exception as e:
            print(f"   ❌ Download failed: {str(e)}")
            return False
        
        # Test 4: Delete test file
        print("\n4. Cleaning up test file...")
        try:
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=test_key)
            print(f"   ✓ Test file deleted successfully")
        except Exception as e:
            print(f"   ⚠ Cleanup failed: {str(e)}")
        
        print("\n" + "="*60)
        print("✓ S3 CONNECTION TEST PASSED")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ S3 Test Failed: {str(e)}")
        logger.error(f"S3 test error: {str(e)}", exc_info=True)
        return False


def test_sqs_connection():
    """Test SQS queue access and message sending capability."""
    print("\n" + "="*60)
    print("TESTING SQS CONNECTION")
    print("="*60)
    
    try:
        if not SQS_QUEUE_URL:
            print("❌ SQS_QUEUE_URL is not configured")
            return False
        
        print(f"✓ Queue Name: {SQS_QUEUE_NAME}")
        print(f"  Queue URL: {SQS_QUEUE_URL}")
        
        sqs_client = get_sqs_client()
        if not sqs_client:
            print("❌ Failed to create SQS client")
            return False
        
        print("✓ SQS client created successfully")
        
        # Test 1: Get queue attributes
        print("\n1. Checking queue access...")
        try:
            response = sqs_client.get_queue_attributes(
                QueueUrl=SQS_QUEUE_URL,
                AttributeNames=['All']
            )
            attrs = response.get('Attributes', {})
            print(f"   ✓ Queue is accessible")
            print(f"   - Messages Available: {attrs.get('ApproximateNumberOfMessages', 'N/A')}")
            print(f"   - Messages In Flight: {attrs.get('ApproximateNumberOfMessagesNotVisible', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Cannot access queue: {str(e)}")
            return False
        
        # Test 2: Send a test message
        print("\n2. Testing message send...")
        test_message = {
            "test": True,
            "work_id": f"test-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "purpose": "Connection test"
        }
        
        try:
            # Check if it's a FIFO queue
            is_fifo = SQS_QUEUE_NAME.endswith('.fifo')
            
            send_params = {
                'QueueUrl': SQS_QUEUE_URL,
                'MessageBody': json.dumps(test_message)
            }
            
            if is_fifo:
                send_params['MessageGroupId'] = 'test-group'
                send_params['MessageDeduplicationId'] = test_message['work_id']
            
            response = sqs_client.send_message(**send_params)
            message_id = response.get('MessageId')
            print(f"   ✓ Message sent successfully")
            print(f"   - Message ID: {message_id}")
        except Exception as e:
            print(f"   ❌ Send failed: {str(e)}")
            return False
        
        print("\n" + "="*60)
        print("✓ SQS CONNECTION TEST PASSED")
        print("="*60)
        print("\n⚠ Note: Test message was sent to the queue.")
        print("  You may want to purge/delete it manually if needed.")
        return True
        
    except Exception as e:
        print(f"\n❌ SQS Test Failed: {str(e)}")
        logger.error(f"SQS test error: {str(e)}", exc_info=True)
        return False


def main():
    """Run all AWS connectivity tests."""
    print("\n" + "="*60)
    print("AWS CONNECTIVITY TEST")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    s3_result = test_s3_connection()
    sqs_result = test_sqs_connection()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"S3 Test:  {'✓ PASSED' if s3_result else '❌ FAILED'}")
    print(f"SQS Test: {'✓ PASSED' if sqs_result else '❌ FAILED'}")
    print("="*60)
    
    if s3_result and sqs_result:
        print("\n✓ ALL TESTS PASSED - AWS credentials are working!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Check your AWS credentials")
        return 1


if __name__ == "__main__":
    sys.exit(main())
