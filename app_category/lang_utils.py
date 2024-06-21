from copy import copy


class TranslateManager:
    def __init__(self, viewset):
        self.viewset = viewset

    def translate_queryset(self, queryset, field_translate, lang):
        queryset_to_update = copy(queryset)
        for el in queryset_to_update:
            self.translate_instance(el, field_translate, lang)

    def translate_instance(self, el, field_translate, lang):
        lang = lang.upper()
        default_value = str(el)
        data_to_translate = el.get_additional_data_transate
        value_to_translate = data_to_translate.get(lang, default_value)
        if value_to_translate == '':
            value_to_translate = default_value
        el.__dict__.update({field_translate: value_to_translate})
