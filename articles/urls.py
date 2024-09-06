from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArticlesView,
    TopicFollowView,
    CreateCommentsView,
    CommentsView,
    ArticleDetailCommentsView,
    FavoriteArticleView
)

router = DefaultRouter()
router.register(r'articles', ArticlesView, basename='article')

urlpatterns = [
    path('', include(router.urls)),
    path('articles/topics/<int:topic_id>/follow/', TopicFollowView.as_view({'post': 'create', 'delete': 'destroy'}), name='topic-follow'),
    path('articles/<int:article_id>/comments/', CreateCommentsView.as_view(), name='create-comment'),
    path('articles/comments/<int:pk>/', CommentsView.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='comment-detail'),
    path('articles/<int:article_id>/detail/comments/', ArticleDetailCommentsView.as_view(), name='article-detail-comments'),
    path('articles/<int:id>/favorite/', FavoriteArticleView.as_view(), name='favorite-article'),

]
