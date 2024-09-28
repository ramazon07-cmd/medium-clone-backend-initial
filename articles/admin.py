<<<<<<< HEAD

# Register your models here.
=======
from .models import Article, Topic, Comment
from django.contrib import admin

admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Topic)
class ClapAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'count')
    search_fields = ('user__username', 'article__title')
    list_filter = ('article',)
>>>>>>> 5daf9e5 (Yangi fayl qo'shildi yoki eski fayl almashtirildi)
