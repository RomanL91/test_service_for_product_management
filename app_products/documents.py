from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from app_products.models import Products


@registry.register_document
class ProductDocument(Document):
    id = fields.IntegerField()
    vendor_code = fields.TextField(
        analyzer="keyword",  # Используем keyword для точного поиска
    )
    name_product = fields.TextField(
        analyzer="autocomplete",
        search_analyzer="autocomplete",
    )
    slug = fields.TextField(analyzer="autocomplete")
    category = fields.ObjectField(
        properties={
            "name_category": fields.TextField(
                analyzer="autocomplete",
            ),
        }
    )
    brand = fields.ObjectField(
        properties={
            "name_brand": fields.TextField(
                analyzer="autocomplete",
            ),
        }
    )
    additional_data = fields.TextField(
        analyzer="autocomplete",
    )
    tag_prod = fields.NestedField(
        properties={
            "tag_text": fields.TextField(
                analyzer="autocomplete",
                search_analyzer="autocomplete",
            ),
        }
    )
    specifications = fields.NestedField(
        properties={
            "name_specification": fields.TextField(
                analyzer="autocomplete",
                search_analyzer="autocomplete",
            ),
            "value_specification": fields.TextField(
                analyzer="autocomplete",
                search_analyzer="autocomplete",
            ),
        }
    )

    class Index:
        name = "products"
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
        model = Products
        fields = []

    def prepare_additional_data(self, instance):
        # Преобразуем JSON-данные в строку с учетом всех непустых значений
        value_list = [str(v) for v in instance.additional_data.values() if v]
        return " ".join(value_list)

    def prepare_category(self, instance):
        """Подготовка категории продукта для индексации"""
        category = instance.category
        if category:
            return {
                "slug": category.slug,
                "name_category": category.name_category,
            }
        return None

    def prepare_brand(self, instance):
        """Подготовка бренда продукта для индексации"""
        brand = instance.brand
        if brand:
            return {
                "name_brand": brand.name_brand,
            }
        return None

    def prepare_tag_prod(self, instance):
        """Подготовка тегов для индексации"""
        return [
            {
                "tag_text": tag.tag_text,
            }
            for tag in instance.tag_prod.all()
        ]

    def prepare_specifications(self, instance):
        """Подготовка характеристик продукта для индексации"""
        return [
            {
                "name_specification": spec.name_specification.__str__(),
                "value_specification": spec.value_specification.__str__(),
            }
            for spec in instance.specifications.all()
        ]
