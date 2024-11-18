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
from elasticsearch import Elasticsearch

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
        # Initialize Elasticsearch client
        #es = Elasticsearch(["http://localhost:9200"])
        es = Elasticsearch(["http://shubhangi-VMware-4:9200"])

        # Initialize Kafka consumer with custom decoder
        consumer = KafkaConsumer(
            'bigdata',
            bootstrap_servers='localhost:9092',
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
                    #logger.info(f"Successfully parsed message: {decoded_message}")
                    try:
                        #print(decoded_message)
                        es.index(index="bigdata", document=decoded_message)
                        #logger.info("Successfully indexed to Elasticsearch")
                    except Exception as e:
                        logger.error(f"Error indexing to Elasticsearch: {str(e)}")
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
