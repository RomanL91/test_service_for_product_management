import json
import pika

from django.core.management.base import BaseCommand

from app_external_products.utils import create_specifications_from_list
from app_products.utils import (
    create_specifications_from_list as create_specifications_from_list_base,
)

# это запуск потрибителя для подкачки характеристик
# python manage.py consumer_spec --host=185.100.67.246 --queue=returned_spec


class Command(BaseCommand):
    help = "Consume order messages from RabbitMQ and save them to DB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--queue",
            type=str,
            default="orders_queue",
            help="RabbitMQ queue name to consume from (default: orders_queue)",
        )
        parser.add_argument(
            "--host",
            type=str,
            default="localhost",
            help="RabbitMQ host (default: localhost)",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=5672,
            help="RabbitMQ port (default: 5672)",
        )
        parser.add_argument(
            "--username",
            type=str,
            default="guest",
            help="RabbitMQ username (default: guest)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="guest",
            help="RabbitMQ password (default: guest)",
        )

    def handle(self, *args, **options):
        queue_name = options["queue"]
        host = options["host"]
        port = options["port"]
        username = options["username"]
        password = options["password"]

        self.stdout.write(
            self.style.SUCCESS(
                f" [*] Connecting to RabbitMQ at {host}:{port}, queue={queue_name}"
            )
        )
        credentials = pika.PlainCredentials(username, password)
        connection_params = pika.ConnectionParameters(
            host=host, port=port, credentials=credentials
        )

        # Создаем соединение и канал
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        # Объявляем очередь на всякий случай (idempotent)
        channel.queue_declare(queue=queue_name, durable=True)

        self.stdout.write(
            self.style.SUCCESS(f" [*] Waiting for messages. Press CTRL+C to exit.")
        )

        # Определяем колбэк на получение сообщений
        def callback(ch, method, properties, body):
            try:
                message_data = json.loads(body)
                self.stdout.write(f" [x] Received message: {message_data}")

                # Сохраняем в БД
                self.save_order_to_db(message_data)

                # Подтверждаем получение
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                self.stderr.write(f" [!] Error processing message: {e}")
                # Не делаем ack => сообщение вернется в очередь

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        connection.close()

    def save_order_to_db(self, message_data: dict):
        print("------------------------")
        print(message_data)
        print(type(message_data))
        print("------------------------")
        idpk = message_data.get("idpk")
        spec_list = message_data.get("spec_list")
        base_prod = message_data.get("base_prod", True)

        if idpk is None or spec_list is None:
            return

        if not base_prod:
            create_specifications_from_list(spec_list, idpk)
        else:
            create_specifications_from_list_base(spec_list, idpk)
