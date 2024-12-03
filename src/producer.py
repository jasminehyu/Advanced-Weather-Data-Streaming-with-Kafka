import time
from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import UnknownTopicOrPartitionError
import weather
import report_pb2

broker = 'localhost:9092'
admin_client = KafkaAdminClient(bootstrap_servers=[broker])

try:
    admin_client.delete_topics(["temperatures"])
    print("Deleted topics successfully")
except UnknownTopicOrPartitionError:
    print("Cannot delete topic/s (may not exist yet)")

time.sleep(3) # Deletion sometimes takes a while to reflect

# TODO: Create topic 'temperatures' with 4 partitions and replication factor = 1

admin_client.create_topics([NewTopic("temperatures",num_partitions=4,replication_factor=1)])
print("Topics:", admin_client.list_topics())

producer = KafkaProducer(bootstrap_servers=[broker],retries=10,acks='all')
# Runs infinitely because the weather never ends
for date, degrees, station_id in weather.get_next_weather(delay_sec=0.1):
    #print(date, degrees, station_id)
    data=report_pb2.Report(date=date,degrees=degrees,station_id=station_id).SerializeToString()
    key=station_id.encode('utf-8')
    producer.send("temperatures",value=data,key=key)
