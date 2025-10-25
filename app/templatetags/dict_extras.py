from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Truy xuất phần tử trong dict theo key"""
    if dictionary is None:
        return None
    try:
        return dictionary.get(str(key)) or dictionary.get(int(key))
    except Exception:
        return None
