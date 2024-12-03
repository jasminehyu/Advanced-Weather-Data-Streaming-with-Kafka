from kafka import KafkaConsumer
from kafka import TopicPartition
import report_pb2
import sys
import json
import os


def load_stats_and_offset(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data, data.get('offset', 0)
    return {}, 0  # Default to empty stats and offset 0 if no file


def temp_stat(partitions):

    broker = "localhost:9092"
    consumer = KafkaConsumer(bootstrap_servers=[broker])
    parts = [TopicPartition("temperatures", p) for p in partitions]
    consumer.assign(parts)
    print(consumer.assignment())
    

    stats_partition={}
    for part in parts:
        file_path = f'partition-{part.partition}.json'
        stat, last_offset = load_stats_and_offset(file_path)
        stats_partition[part.partition] = {
            "last_offset": last_offset,
            "stat": stat
        }
        consumer.seek(part,last_offset)  # Seek to the last known offset
        print(last_offset)
        
    while True:
        batch=consumer.poll(1000)
        for tp,messages in batch.items():
            
            partition = tp.partition  # Current partition
            current_stat = stats_partition[partition]["stat"]
            print(f"Processing partition {partition}")
            
            for msg in messages:
                report=report_pb2.Report.FromString(msg.value)
                station=report.station_id
                if station not in current_stat:
                    current_stat[station]={
                        "count": 1,
                        "sum": report.degrees,
                        "avg": report.degrees,
                        "start": report.date,
                        "end": report.date}

                else:
                    current_stat[station]['count'] += 1
                    current_stat[station]['sum'] += report.degrees
                    current_stat[station]['avg'] = current_stat[station]['sum']/current_stat[station]['count']
                    current_stat[station]['start'] = min(current_stat[station]['start'], report.date)
                    current_stat[station]['end'] = max(current_stat[station]['end'], report.date)
                
            print("fill out offset")
            stats_partition[partition]['last_offset'] = consumer.position(tp)


            path = f'/src/partition-{partition}.json'
            path2 = path + ".tmp"
            with open(path2, "w") as f:
                # TODO: write the data
                json.dump({
                    "offset": stats_partition[partition]['last_offset'],
                    **current_stat  # Merge the station stats with the offset
                }, f,indent=4)
            os.rename(path2, path)

        
                
                               

if __name__ == "__main__":
    partitions= list(map(int, sys.argv[1:]))
    temp_stat(partitions)
