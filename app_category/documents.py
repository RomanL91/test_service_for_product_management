from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from app_category.models import Category


@registry.register_document
class CategoryDocument(Document):
    name_category = fields.TextField(
        analyzer="autocomplete", search_analyzer="standard"
    )
    slug = fields.TextField(analyzer="autocomplete", search_analyzer="standard")
    # Индексируем additional_data как строку для поиска по любому значению внутри JSON
    additional_data = fields.TextField(analyzer="standard")

    class Index:
        name = "categories"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "filter": {
                    "edge_ngram_filter": {
                        "type": "edge_ngram",
                        "min_gram": 2,
                        "max_gram": 20,
                    }
                },
                "analyzer": {
                    "autocomplete": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "edge_ngram_filter"],
                    }
                },
            },
        }

    class Django:
        model = Category
        fields = []

    def prepare_additional_data(self, instance):
        # Преобразуем JSON-данные в строку с учетом всех непустых значений
        value_list = [str(v) for v in instance.additional_data.values() if v]
        return " ".join(value_list)
