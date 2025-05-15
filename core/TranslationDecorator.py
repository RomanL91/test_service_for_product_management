from typing import Type

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.RabbitMQRepository import rabbitmq_repo


def register_for_translation(source_field: str, target_field: str):
    def decorator(model_class: Type):
        if not hasattr(model_class, "_translation_mappings"):
            model_class._translation_mappings = []
        model_class._translation_mappings.append((source_field, target_field))

        @receiver(post_save, sender=model_class)
        def handle_translation(instance, **kwargs):
            for source, target in model_class._translation_mappings:
                source_value = getattr(instance, source, None)
                target_value = getattr(instance, target, {})

                if source_value and isinstance(target_value, dict):
                    for lang, text in target_value.items():
                        if not text:

                            name_app = instance.__class__.__module__.split(".")[0]
                            message = {
                                # "model_name": instance.__class__.__name__,
                                "model_name": f"{name_app}.{instance.__class__.__name__}",
                                "instance_id": instance.id,
                                "source_field": source,
                                "target_field": target,
                                "text": source_value,
                                "target_lang": lang,
                            }
                            rabbitmq_repo.send_message(
                                "translation_queue",
                                message,
                            )

        return model_class

    return decorator
