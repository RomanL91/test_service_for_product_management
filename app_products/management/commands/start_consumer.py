from django.core.management.base import BaseCommand

from core.RabbitMQRepository import rabbitmq_repo
from core.TranslationUpdateService import TranslationUpdateService


class Command(BaseCommand):
    help = "Запуск consumer для response_translation_queue"

    def handle(self, *args, **options):
        print("✅ Запуск consumer для response_translation_queue")
        service = TranslationUpdateService(rabbitmq_repo)
        service.start_consumer()
