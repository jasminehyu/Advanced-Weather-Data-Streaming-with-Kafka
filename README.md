# Weather Data Streaming with Kafka

## Project Overview
This project demonstrates the implementation of a data pipeline using Apache Kafka to manage and process real-time weather data. 
The goal is to capture daily temperature readings from multiple stations and utilize this data to produce insightful summaries through a series of Python applications interacting with a Kafka stream.


## Technical Implementation

## Kafka Setup
The project utilizes Docker to run a Kafka broker, ensuring a simplified setup and isolation of the environment.
The Docker container hosts the Kafka broker alongside the Python applications designed to produce and consume the weather data.

```
# To build the image
docker build . -t p7

# TO run the Kafka broker in the background using:
docker run -d -v ./src:/src --name=p7 p7
```

## Kafka Producer
A Python script (producer.py) acts as a Kafka producer, generating weather data in real-time, which simulates the reception of data from various weather stations. 
This script handles the creation and management of the Kafka topic and ensures data integrity through custom configurations that manage retries and acknowledgments.

```
# To run the producer program
docker exec -d -w /src p7 python3 producer.py
```


## Kafka Consumer
Multiple consumer scripts are developed to handle data consumption from the Kafka stream. The primary consumer script (consumer.py) is designed to compute and store weather statistics in JSON format. It implements sophisticated techniques to handle partition assignments manually and ensures crash recovery by maintaining read offsets.

```
# To run the consumer program (for partition 0, 2)
docker exec -it -w /src p7 python3 consumer.py 0 2
```


Here is an example `partition-N.json` file with two stations:

```json
{
  "StationD": {
    "count": 34127,
    "sum": 1656331612.266097,
    "avg": 48534.34559926442,
    "start": "1990-01-02",
    "end": "2437-05-01"
  },
  "StationB": {
    "count": 34466,
    "sum": 1700360597.4081032,
    "avg": 49334.433859690806,
    "start": "1990-01-07",
    "end": "2437-05-09"
  }
}
```

Each `partition-N.json` file should have a key for each `station_id` seen in that
partition. Under each `station_id`, you have the following statistics describing messages for that station:

* `count`: the number of days for which data is available for the corresponding `station_id`.
* `sum`: sum of temperatures seen so far (yes, this is an odd metric by itself)
* `avg`: the `sum/count`. This is the only reason we record the sum - so we can recompute the average on a running basis without having to remember and loop over all temperatures each time the file is updated
* `start`: the date of the *first* measurement for the corresponding
station id.
* `end`: the date of the *last* measurement for the corresponding
station id.

## Debugging and Monitoring
A debugging script (debug.py) is also part of the project to monitor the data flow through the Kafka stream and verify 
the integrity of data production and consumption processes.

```
# To run the debug program
docker exec -it -w /src p7 python3 debug.py
```

Example:
```
...
{'station_id': 'StationC', 'date': '2008-12-17', 'degrees': 35.2621, 'partition': 2}
{'station_id': 'StationC', 'date': '2008-12-20', 'degrees': 13.4537, 'partition': 2}
{'station_id': 'StationE', 'date': '2008-12-24', 'degrees': 35.3709, 'partition': 2}
{'station_id': 'StationA', 'date': '2008-07-06', 'degrees': 80.1362, 'partition': 3}
...
```

## Challenges and Solutions
- **Streaming Data Handling:** The project employs "exactly once" semantics to ensure reliable message processing in a real-time streaming context.
- **Data Integrity:** Advanced settings in Kafka producers ensure that data is consistently acknowledged across all replicas, minimizing data loss.
- **Crash Recovery:** Consumer scripts are equipped with mechanisms to recover from crashes, including checkpointing and restarting from the last known good state.


## System Architecture
The system architecture revolves around Docker containers, Kafka for message queuing, and Python for data processing. 
This setup exemplifies a robust infrastructure capable of handling high-throughput data streams with resilience and scalability.

## Conclusion
This project serves as a showcase of applying modern data streaming techniques to solve practical problems in data handling and analysis. 
The integration of Kafka with Python provides a flexible and powerful solution for real-time data processing challenges.
