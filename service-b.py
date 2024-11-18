#!/usr/bin/env python3
import json
import time
import uuid
from datetime import datetime

def register_service(service_name, log_file):
    registration = {
        "node_id": str(uuid.uuid4()),
        "message_type": "REGISTRATION",
        "service_name": service_name,
        "timestamp": datetime.utcnow().isoformat()
    }
    write_log(log_file, registration)

def log_message(log_level, message, service_name, log_file):
    log = {
        "log_id": str(uuid.uuid4()),
        "node_id": service_name,
        "log_level": log_level,
        "message_type": "LOG",
        "message": message,
        "service_name": service_name,
        "timestamp": datetime.utcnow().isoformat()
    }
    write_log(log_file, log)

def send_heartbeat(service_name, log_file):
    heartbeat = {
        "node_id": service_name,
        "message_type": "HEARTBEAT",
        "status": "UP",
        "timestamp": datetime.utcnow().isoformat()
    }
    write_log(log_file, heartbeat)

def write_log(log_file, log_data):
    with open(log_file, "a") as file:
        file.write(json.dumps(log_data) + "\n")

def main():
    #service_name = f"Service-{uuid.uuid4()}"
    #log_file = f"./logs/{service_name}.log"
    service_name = "Service-b"
    log_file = "/tmp/b.log"
    register_service(service_name, log_file)

    warn_trigger_count = 0
    err_trigger_count = 0
    while True:
        if warn_trigger_count == 10:
          log_message("WARN", "Service having warning.", service_name, log_file)
          warn_trigger_count = 0

        if err_trigger_count == 20:
          log_message("ERROR", "Service having error.", service_name, log_file)
          err_trigger_count = 0

        log_message("INFO", "Service running smoothly.", service_name, log_file)
        send_heartbeat(service_name, log_file)
        warn_trigger_count += 1
        err_trigger_count += 1
        time.sleep(5)

if __name__ == "__main__":
    main()
