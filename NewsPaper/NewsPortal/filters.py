# NewsPortal/filters.py
import django_filters
from .models import Post, Author
from django import forms

class PostFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains', 
        label='Название'
    )
    author_name = django_filters.CharFilter(
        field_name='author__user__username', lookup_expr='icontains',
        label='Автор'
    )
    date_after = django_filters.DateFilter(
        field_name='time_create', lookup_expr='gte',
        label='Позже даты',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = ['name', 'author_name', 'date_after']