from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')
for _ in range(100):
    producer.send('myTopic', b'some_message_bytes')
