import pika
import json

from django.conf import settings


class RabbitMQRepository:
    _instance = None
    _initialized_queues = set()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RabbitMQRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, url: str):
        if not hasattr(self, "url"):
            self.url = url
            self.connection = None
            self.channel = None

    def connect(self):
        if not self.connection or self.connection.is_closed:
            params = pika.URLParameters(self.url)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
        return self.channel

    def declare_queue(self, queue_name: str):
        if queue_name not in self._initialized_queues:
            channel = self.connect()
            channel.queue_declare(queue=queue_name, durable=True)
            self._initialized_queues.add(queue_name)
            print(f"✅ Очередь '{queue_name}' инициализирована.")

    def send_message(self, queue_name: str, message: dict):
        try:
            channel = self.connect()
            self.declare_queue(queue_name)
            channel.basic_publish(
                exchange="", routing_key=queue_name, body=json.dumps(message)
            )
            print(f"✅ Сообщение отправлено в очередь '{queue_name}': {message}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения в RabbitMQ: {e}")


rabbitmq_repo = RabbitMQRepository(settings.RABBITMQ)
