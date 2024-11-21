from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArticlesView,
    TopicFollowView,
    CreateCommentsView,
    CommentsView,
    ArticleDetailCommentsView,
    FavoriteArticleView,
    ClapView,
    ReportArticleView,
    FAQListView
)
from users.views import PinView, ArchiveView

router = DefaultRouter()
router.register(r'articles', ArticlesView, basename='article')

urlpatterns = [
    path('articles/topics/<int:topic_id>/follow/', TopicFollowView.as_view({'post': 'create', 'delete': 'destroy'}), name='topic-follow'),
    path('articles/<int:article_id>/comments/', CreateCommentsView.as_view(), name='create-comment'),
    path('articles/comments/<int:pk>/', CommentsView.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='comment-detail'),
    path('articles/<int:article_id>/detail/comments/', ArticleDetailCommentsView.as_view(), name='article-detail-comments'),
    path('articles/<int:id>/favorite/', FavoriteArticleView.as_view(), name='favorite-article'),
    path('articles/<int:id>/clap/', ClapView.as_view(), name='article-clap'),
    path('articles/<int:id>/archive/', ArchiveView.as_view(), name='article-archive'),
    path('articles/<int:id>/pin/', PinView.as_view(), name='pin_article'),
    path('articles/<int:id>/unpin/', PinView.as_view(), name='unpin_article'),
    path('articles/<int:id>/report/', ReportArticleView.as_view(), name='report_article'),
    path('articles/faqs/', FAQListView.as_view(), name='faq_article'),
    path('', include(router.urls)),
]
