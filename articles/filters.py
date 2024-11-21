import django_filters
from .models import Article
from django.db import models
from django.db.models import Q
from users.models import ReadingHistory

class ArticleFilter(django_filters.FilterSet):
    is_recommend = django_filters.BooleanFilter(method='filter_is_recommend') # method orqali funksiyalarga ulash
    search = django_filters.CharFilter(method='filter_by_search') # method orqali funksiyalarga ulash
    is_reading_history = django_filters.BooleanFilter(method='filter_reading_history') # method orqali funksiyalarga ulash
    is_user_favorites = django_filters.BooleanFilter(method='filter_user_favorites') # method orqali funksiyalarga ulash


    class Meta:
        model = Article
        fields = ['is_recommend', 'is_reading_history']

    def filter_is_recommend(self, queryset, name, value):
        if value:
            return queryset.filter(models.Q(more_recommend__isnull=False) & models.Q(less_recommend__isnull=True)).distinct()
        return queryset

    def filter_reading_history(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            user_history = ReadingHistory.objects.filter(user=self.request.user)
            article_ids = user_history.values_list('article_id', flat=True)
            return queryset.filter(id__in=article_ids)
        return queryset

    def filter_by_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(summary__icontains=value) |
            Q(content__icontains=value) |
            Q(topics__name__icontains=value)
        ).distinct()

    def filter_user_favorites(self, queryset, name, value):
        if value:
            user = self.request.user
            return queryset.filter(favorited_by__user=user)
        return queryset
