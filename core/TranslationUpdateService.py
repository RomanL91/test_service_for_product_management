import json
from django.apps import apps

from core.RabbitMQRepository import RabbitMQRepository


class TranslationUpdateService:
    def __init__(self, rabbitmq_repo: RabbitMQRepository):
        self.rabbitmq_repo = rabbitmq_repo
        self.queue_name = "response_translation_queue"
        self.rabbitmq_repo.declare_queue(self.queue_name)

    def process_translation_update(self, channel, method, properties, body):
        try:
            payload = json.loads(body.decode())
        except json.JSONDecodeError:
            print("❌ Ошибка при декодировании сообщения")
            return

        model_name = payload.get("model_name")
        instance_id = payload.get("instance_id")
        # source_field = payload.get("source_field")
        target_field = payload.get("target_field")
        translated_text = payload.get("text")
        target_lang = payload.get("target_lang")

        if not all(
            [model_name, instance_id, target_field, translated_text, target_lang]
        ):
            print(f"❌ Неверное сообщение: {payload}")
            return

        try:
            model = apps.get_model(model_name)
        except LookupError:
            print(f"❌ Модель '{model_name}' не найдена")
            return

        try:
            instance = model.objects.get(id=instance_id)
        except model.DoesNotExist:
            print(f"❌ Экземпляр с id={instance_id} не найден")
            return

        target_data = getattr(instance, target_field, {})
        if isinstance(target_data, dict):
            target_data[target_lang] = translated_text
            # Обновляем поле без вызова save() для предотвращения зацикливания
            model.objects.filter(id=instance_id).update(**{target_field: target_data})
            print(f"✅ Обновлено: {instance}")
        else:
            print(f"❌ Поле '{target_field}' не является JSONField")

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def start_consumer(self):
        channel = self.rabbitmq_repo.connect()
        channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.process_translation_update
        )
        print(f"✅ Слушаем очередь '{self.queue_name}'...")
        channel.start_consuming()
