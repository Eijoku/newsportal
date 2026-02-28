from django import template
import re

register = template.Library()

# Встроенный список запрещённых слов (или импортируйте из другого модуля)
BAD_WORDS = ['редиска', 'тутук']

@register.filter
def censor(value):
    """
    Фильтр, заменяющий запрещённые слова на звёздочки,
    оставляя первый символ видимым.
    """
    if not isinstance(value, str):
        return value

    pattern = r'\b(' + '|'.join(re.escape(word) for word in BAD_WORDS) + r')\b'
    
    def replace_with_stars(match):
        word = match.group()
        # Оставляем первый символ
        return word[0] + '*' * (len(word) - 1)
    
    return re.sub(pattern, replace_with_stars, value, flags=re.IGNORECASE)