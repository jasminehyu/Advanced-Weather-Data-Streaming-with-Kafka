from kafka import KafkaConsumer
import report_pb2

broker = "localhost:9092"
consumer = KafkaConsumer(bootstrap_servers=[broker], group_id="debug")
consumer.subscribe(["temperatures"])
while True:
    batch=consumer.poll(1000)
    for topic_partition, messages in batch.items():
        for msg in messages:
            report=report_pb2.Report.FromString(msg.value)
            print({
                'station_id':report.station_id,
                'date': report.date,
                'degrees':report.degrees,
                'partition':topic_partition.partition})
