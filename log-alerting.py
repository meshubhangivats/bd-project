#!/usr/bin/env python3
import sys 
import logging
from typing import Any, Optional
import json

# Handle Python 3.12+ kafka.vendor.six.moves compatibility
if sys.version_info >= (3, 12, 0): 
    import six 
    sys.modules['kafka.vendor.six.moves'] = six.moves

from kafka import KafkaConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def safe_decode(message_value: bytes) -> Optional[dict]:
    """Safely decode and parse Kafka message value."""
    try:
        # First, let's see what the raw message looks like
        raw_string = message_value.decode('utf-8', errors='replace')
        #logger.info(f"Raw message: {raw_string}")
                            
        # Try to parse as JSON
        return json.loads(raw_string)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        logger.error(f"Raw message that caused error: {raw_string}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while decoding: {str(e)}")
        return None
def main():
    try:

        # Initialize Kafka consumer with custom decoder
        consumer = KafkaConsumer(
            'bigdata',
            bootstrap_servers='shubhangi-VMware-3:9092',
            auto_offset_reset='earliest',
            # Use bytes decoder instead of direct JSON decoder
            value_deserializer=lambda x: x  # Just return raw bytes
        )

        #logger.info("Starting to consume messages...")

        for message in consumer:
            if message.value:
                # Decode and parse the message
                decoded_message = safe_decode(message.value)

                if decoded_message:
                    try:
                        json_string = decoded_message['message']
                        data = json.loads(json_string)
                        #print(data['log_level'])
                        if data['message_type'] == 'LOG' and data['log_level'] in ['WARN', 'ERROR', 'FATAL']:
                           print(f"ALERT: {data['log_level']} from {data['service_name']} - {data['message']}")
                    except Exception as e:
                        #logger.error(f"Error {str(e)}")
                        pass 
            else:
                logger.warning("Received empty message")

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
    finally:
        consumer.close()
        logger.info("Kafka consumer closed")

if __name__ == "__main__":
    main()
