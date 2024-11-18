#!/usr/bin/env python3
import sys 
import logging
from typing import Any, Optional
import json
from datetime import datetime, timedelta
import time  # Added for periodic checks

# Handle Python 3.12+ kafka.vendor.six.moves compatibility
if sys.version_info >= (3, 12, 0): 
    import six 
    sys.modules['kafka.vendor.six.moves'] = six.moves

from kafka import KafkaConsumer

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

def safe_decode(message_value: bytes) -> Optional[dict]:
    """Safely decode and parse Kafka message value."""
    try:
        raw_string = message_value.decode('utf-8', errors='replace')
        return json.loads(raw_string)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while decoding: {str(e)}")
        return None

heartbeat_status = {}
last_check_time = datetime.utcnow()
HEARTBEAT_TIMEOUT = 10  # seconds
CHECK_INTERVAL = 5      # seconds

def check_node_status():
    """Check the status of all nodes and log warnings for potentially failed nodes."""
    global last_check_time
    now = datetime.utcnow()
    
    # Only run check if enough time has passed since last check
    if (now - last_check_time).total_seconds() < CHECK_INTERVAL:
        return
    
    last_check_time = now
    #logger.info(f"Checking node status at {now}")
    #logger.info(f"Current heartbeat status: {heartbeat_status}")
    
    if not heartbeat_status:
        #logger.warning("No nodes have reported heartbeats yet")
        return
    
    for node, last_seen in list(heartbeat_status.items()):
        time_since_last_heartbeat = now - last_seen
        
        if time_since_last_heartbeat > timedelta(seconds=HEARTBEAT_TIMEOUT):
            logger.warning(
                f"ALERT: Node {node} may have failed. "
                f"Last seen at {last_seen} "
                f"({time_since_last_heartbeat.total_seconds():.1f} seconds ago)"
            )
            del heartbeat_status[node]
        #else:
        #    logger.info(
        #        f"Node {node} is healthy, last seen {time_since_last_heartbeat.total_seconds():.1f} seconds ago"
        #    )

def main():
    try:
        # Initialize Kafka consumer with custom decoder
        consumer = KafkaConsumer(
            'bigdata',
            bootstrap_servers='shubhangi-VMware-3:9092',
            auto_offset_reset='earliest',
            value_deserializer=lambda x: x,  # Just return raw bytes
            consumer_timeout_ms=1000  # Allow periodic checking even without messages
        )
        
        logger.info("Kafka consumer initialized and waiting for messages...")
        
        while True:
            #message_count = 0
            messages = consumer.poll(timeout_ms=1000)
            
            for topic_partition, msgs in messages.items():
                for message in msgs:
                    #message_count += 1
                    if message.value:
                        decoded_message = safe_decode(message.value)
                        if decoded_message:
                            try:
                                json_string = decoded_message['message']
                                data = json.loads(json_string)
                                
                                if data['message_type'] == 'HEARTBEAT':
                                    node_id = data['node_id']
                                    heartbeat_status[node_id] = datetime.utcnow()
                                    logger.info(f"Heartbeat received for node {node_id}")
                            except KeyError as e:
                                logger.error(f"Missing key in message: {str(e)}")
                            except Exception as e:
                                logger.error(f"Error processing message: {str(e)}")
                    else:
                        logger.warning("Received empty message")
            
            # Check node status periodically, even if no messages are received
            check_node_status()
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.1)
            
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
