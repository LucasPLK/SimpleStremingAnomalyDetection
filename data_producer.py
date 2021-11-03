import pika
import numpy as np
from threading import Thread, Lock
import json
import time

class DataProducer():

    def __init__(self):
        """

        """
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()


    def publish(self, t: float):
        """

        """
        while(True):

            anomaly = np.random.rand() > 0.75

            for i in np.arange(0, 2*np.pi, t):
                time.sleep(0.2)
                rand = np.random.rand()
                body = {
                    'time': time.time(),
                    'sin': np.sin(i)*np.random.rand()/10,
                    'sawtooth': i,
                    'random': rand,
                    'sqrt': np.sqrt(i),
                    'equation': np.sin(i)*2+i+rand+np.sqrt(i)*3 if not anomaly else np.sin(i)
                }

                self.channel.basic_publish(exchange='amq.topic',
                            routing_key='equation',
                            body=json.dumps(body))

   
    def start(self):
        """

        """
        try:
            self.publish(0.2)

            
        except KeyboardInterrupt:
            print('Rabbit connection closed')
            try:
                self.connection.close()
            except Exception as ex:
                pass


if __name__ == '__main__':
    """
    
    """
    data_producer = DataProducer()
    data_producer.start()
