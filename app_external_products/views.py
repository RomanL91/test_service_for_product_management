import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .utils import update_offers  # Импортируем вашу функцию обновления
from .tests import DATATEST


@csrf_exempt  # отключаем проверку CSRF для примера (в реальном проекте настройте безопасность)
@require_POST  # принимаем только POST-запрос
def offers_endpoint(request):
    """
    Эндпоинт для приёма данных offers (JSON),
    обновления/создания записей в модели и возврата результата.
    """
    try:
        # Попытка считать и распарсить JSON
        # data = json.loads(request.body.decode("utf-8"))
        data = DATATEST
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": str(e)}, status=400)

    try:
        # Вызываем функцию, которая создаёт/обновляет данные в БД
        update_offers(data)
    except Exception as e:
        # На случай любых непредвиденных ошибок в процессе записи в базу
        return JsonResponse({"error": str(e)}, status=500)

    # Успешный ответ
    return JsonResponse({"status": "ok"}, status=200)
