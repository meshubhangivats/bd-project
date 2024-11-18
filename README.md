Here is the services layout 

Ubuntu-1 VM
- /home/shubhangi
  - service-a.py
  - service-b.py
  - service-c.py
- Install Fluentd by following log-accumulator-installation-configuration file
  - Log accumulator running as service

Ubuntu-3 VM
- Install Kafka
  - Kafka running as service
- /home/shubhangi
  - log_storage.py

Ubuntu-4 VM
- Install Elasticsearch by following elasticsearch-installation-configuration file
  - Elasticsearch running as a service
- Install Kibana
  - Browse Elasticsearch logs using kibana discover view

Ubuntu-5 VM
- /home/shubhangi
  - heartbeat-monitoring.py
  - log-alreting.py
  


    

