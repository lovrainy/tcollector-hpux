#!/usr/bin/env python

from kafka import KafkaProducer


pro = KafkaProducer(bootstrap_servers=["10.1.248.12:9092"], api_version=(0,11))
pro.send('testhp', b'11111111111111111111111111111111')
print('=============================')
