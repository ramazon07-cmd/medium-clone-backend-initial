from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from django_redis import get_redis_connection
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import Article, TopicFollow, Topic, Comment, Favorite, Clap, Report
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from .filters import ArticleFilter
from rest_framework.decorators import action
from users.models import ReadingHistory
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .serializers import ArticleSerializer, CommentSerializer, ArticleDetailCommentsSerializer, ClapSerializer, ReportSerializer
from rest_framework.views import APIView
class ArticlesView(viewsets.ModelViewSet):
    queryset = Article.objects.filter(status__iexact="publish")
    serializer_class = ArticleSerializer
    http_method_names = ['get', 'post', 'patch', 'delete'] # method nomlari
    permission_classes = [IsAuthenticated] # permissionlar
    filter_backends = [DjangoFilterBackend] # filters qo'shish uchun ishlatildi
    filterset_class = ArticleFilter # filtersdan chaqirish kerak
    search_fields = ['title', 'summary', 'content', 'topics__name']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleSerializer
        return ArticleSerializer

    def create(self, request, *args, **kwargs):
        author = request.user
        if not author.is_authenticated:
            return Response({'error': 'Xato mavjud'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        data['author'] = author.id # authorni aniqlash

        serializer = self.get_serializer(data=data) # ma'lumot kiritish
        if serializer.is_valid():
            self.perform_create(serializer) # ma'lumot yaratish
            response_data = serializer.data
            headers = self.get_success_headers(response_data)

            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        article = self.get_object()
        article.reads_count += 1
        article.save()
        return Response({"detail": "Maqolani o'qish soni ortdi."}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        article = self.get_object()
        article.views_count += 1
        article.save()
        if request.user.is_authenticated:
            ReadingHistory.objects.get_or_create(user=request.user, article=article)
        return response

    @action(detail=True, methods=['patch'])
    def patch(self, request, *args, **kwargs):
        redis_conn = get_redis_connection('default')
        redis_conn.set('test_key', 'test_value', ex=3600)
        cached_value = redis_conn.get('test_key')
        print(cached_value)
        response = super().partial_update(request, *args, **kwargs)
        print(response.data)
        return Response(response.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def reading_history(self, request):
        self.queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        article = self.get_object()
        article.status = "trash"
        article.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TopicFollowView(viewsets.ViewSet):
    def create(self, request, topic_id=None):
        user = request.user
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response({"detail": "Hech qanday mavzu berilgan soʻrovga mos kelmaydi."}, status=status.HTTP_404_NOT_FOUND)

        if TopicFollow.objects.filter(user=user, topic=topic).exists():
            return Response({"detail": f"Siz allaqachon '{topic.name}' mavzusini kuzatyapsiz."}, status=status.HTTP_200_OK)

        TopicFollow.objects.create(user=user, topic=topic)
        return Response({"detail": f"Siz '{topic.name}' mavzusini kuzatyapsiz."}, status=status.HTTP_201_CREATED)

    def destroy(self, request, topic_id=None):
        user = request.user
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response({"detail": "Hech qanday mavzu berilgan soʻrovga mos kelmaydi."}, status=status.HTTP_404_NOT_FOUND)

        follow = TopicFollow.objects.filter(user=user, topic=topic).first()
        if not follow:
            return Response({"detail": f"Siz '{topic.name}' mavzusini kuzatmaysiz."}, status=status.HTTP_404_NOT_FOUND)

        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CreateCommentsView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated] # serializerdan foydalanish sharti

    def perform_create(self, serializer):
        article_id = self.kwargs.get('article_id')
        article = get_object_or_404(Article, pk=article_id)

        if article.status != 'publish':
            raise NotFound("This article is inactive and cannot accept comments.")

        # Serializerni user va article bilan saqlash
        serializer.save(user=self.request.user, article=article)

class CommentsView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated] # serializerdan foydalanish sharti

    def partial_update(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            raise PermissionDenied("You do not have permission to perform this action.")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            raise PermissionDenied("You do not have permission to perform this action.")
        return super().destroy(request, *args, **kwargs)

class ArticleDetailCommentsView(generics.ListAPIView):
    serializer_class = ArticleDetailCommentsSerializer

    def get_queryset(self):
        article_id = self.kwargs.get('article_id')
        return Article.objects.filter(pk=article_id).prefetch_related('article_comments')

class FavoriteArticleView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated] # serializerdan foydalanish sharti

    def post(self, request, *args, **kwargs):
        article_id = self.kwargs.get('id')
        article = Article.objects.filter(id=article_id).first()

        if not article:
            raise NotFound(detail="Maqola topilmadi.")

        favorite, created = Favorite.objects.get_or_create(user=request.user, article=article)

        if created:
            return Response({"detail": "Maqola sevimlilarga qo'shildi."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Maqola sevimlilarga allaqachon qo'shilgan."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        article_id = self.kwargs.get('id')
        article = Article.objects.filter(id=article_id).first()

        if not article:
            raise NotFound(detail="Maqola topilmadi.")

        favorite = Favorite.objects.filter(user=request.user, article=article).first()

        if favorite:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Maqola topilmadi."}, status=status.HTTP_404_NOT_FOUND)

MAX_CLAPS = 50
class ClapView(APIView):
    permission_classes = [IsAuthenticated] # serializerdan foydalanish sharti

    def post(self, request, id):
        article = get_object_or_404(Article, pk=id)

        clap, created = Clap.objects.get_or_create(user=request.user, article=article)

        if created:
            clap.count = 1
        else:
            if clap.count >= MAX_CLAPS:
                return Response({"count": MAX_CLAPS}, status=status.HTTP_201_CREATED)
            else:
                clap.count += 1

        clap.save()
        return Response({"count": clap.count}, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        article = get_object_or_404(Article, pk=id)
        claps_deleted, _ = Clap.objects.filter(user=request.user, article=article).delete()

        if claps_deleted > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = Report.objects.filter(user=user, read_at__isnull=True)

        paginator = ReportPagination()
        paginated_notifications = paginator.paginate_queryset(notifications, request)

        serializer = ReportSerializer(paginated_notifications, many=True)
        return paginator.get_paginated_response(serializer.data)

# lookup_field ni urlga bog'liqlgi bor

class ReportArticleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user = request.user
        article = Article.objects.filter(id=id).exclude(status='trash').first()

        if not article:
            return Response({"detail": "No Article matches the given query."}, status=status.HTTP_404_NOT_FOUND)

        if article.status == 'trash':
            return Response({"detail": "Maqola topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if article.status == 'draft':
            return Response({"detail": "No Article matches the given query."}, status=status.HTTP_404_NOT_FOUND)

        if Report.objects.filter(user=user, article=article).exists():
            return Response(["Ushbu maqola allaqachon shikoyat qilingan."], status=status.HTTP_400_BAD_REQUEST)

        report = Report.objects.create(user=user, article=article, created_at=timezone.now())

        report_count = Report.objects.filter(article=article).count()

        if report_count >= 3:
            article.status = 'trash'
            article.save()
            return Response({"detail": "Maqola bir nechta shikoyatlar tufayli olib tashlandi."}, status=status.HTTP_200_OK)

        return Response({"detail": "Shikoyat yuborildi."}, status=status.HTTP_201_CREATED)
