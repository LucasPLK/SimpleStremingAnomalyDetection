import pika
from collections import deque
import json
import matplotlib.pyplot as plt
import joblib


class AnomalyDetection():
    """
        Classe para detecção de anomalias em tempo real
    """
    def __init__(self):
        
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='digitalTwin', arguments={'x-message-ttl' : 10})
        self.channel.queue_bind(exchange='amq.topic', queue='digitalTwin', routing_key='#.#')

        queue_size = 100 # Quantidade máxima de dados que será armazenada na fila
        
        # declaração das filas que são utilizadas para armazenar os dados recebidos via streaming
        self.sin = deque(maxlen=queue_size)
        self.sawtooth = deque(maxlen=queue_size)
        self.random = deque(maxlen=queue_size)
        self.sqrt = deque(maxlen=queue_size)
        self.time = deque(maxlen=queue_size)
        self.equation = deque(maxlen=queue_size)

        # Carregamento do modelo de digital Twin Treinado
        self.model = joblib.load('model.joblib')
        self.params = joblib.load('params.joblib')

        # Limite aceitável do resíduo para considerar o dado normal
        self.limit = self.params['mean']+3*self.params['std']


    def receiver_callback(self, ch, method, properties, body):
        """
            Callback de recebimento e processamento do dado vindo do RabbitMQ
        """
        equation_color = 'green'
        equation_lw = 3
        message = json.loads(body)
        self.sin.append(message['sin'])
        self.sawtooth.append(message['sawtooth'])
        self.random.append(message['random'])
        self.sqrt.append(message['sqrt'])
        self.time.append(message['time'])
        self.equation.append(message['equation'])


        # Predição do valor esperado com os dados recebidos
        predict = self.model.predict([[self.sin[-1], self.sawtooth[-1], self.sqrt[-1]]])
        residual = self.equation[-1] - predict

        if abs(residual) > self.limit:
            # Residuo fora dos limites máximos indica uma anomalia
            equation_color = 'red'
            equation_lw = 6
            plt.title('ANOMALIA', fontsize=20, fontdict={'color':'red'})
        else:
            plt.title('Normal', fontsize=12,fontdict={'color':'green'})
        
        # Plotagem do gráfico em tempo real
        plt.plot(self.time, self.sin, c='black', label='sin')
        plt.plot(self.time, self.sawtooth, c='blue', label='sawtooth')
        plt.plot(self.time, self.random, c='orange', label='random')
        plt.plot(self.time, self.sqrt, c='gray', label='sqrt')
        plt.plot(self.time, self.equation, c=equation_color,  label='equation', lw=equation_lw)
        plt.legend(loc='upper right')
        plt.grid()
        plt.pause(0.2)
        plt.clf()




    def consume_data(self):
        """
        Função que declara e inicia o consumidor de dados do RabbitMQ
        """
        self.channel.basic_consume(queue='digitalTwin',
                                auto_ack=True,
                                on_message_callback=self.receiver_callback)

        self.channel.start_consuming()

if __name__ == '__main__':

    anomaly_detection = AnomalyDetection()
    anomaly_detection.consume_data()
