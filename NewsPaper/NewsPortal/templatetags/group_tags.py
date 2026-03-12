from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def in_group(context, group_name):
    user = context['request'].user
    return user.is_authenticated and user.groups.filter(name=group_name).exists()
