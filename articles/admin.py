from .models import Article, Topic, Comment, Report
from django.contrib import admin

admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Topic)
admin.site.register(Report)
class ClapAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'count')
    search_fields = ('user__username', 'article__title')
    list_filter = ('article',)
