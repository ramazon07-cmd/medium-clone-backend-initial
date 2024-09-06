from rest_framework import serializers
from .models import Article, Topic, TopicFollow, Comment
from users.models import CustomUser

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'is_active']

class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'status', 'content', 'thumbnail', 'topic_ids', 'summary', 'created_at', 'updated_at', 'topics', 'claps']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

class ArticleCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    topics = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), many=True)

    class Meta:
        model = Article
        fields = ['title', 'summary', 'content', 'thumbnail', 'user', 'topics']

    def create(self, validated_data):
        return super().create(validated_data)

class ArticleDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    topics = TopicSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'user', 'title', 'summary', 'content', 'status', 'thumbnail', 'topics', 'created_at', 'updated_at']

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'middle_name': obj.user.middle_name,
            'email': obj.user.email,
            'avatar': obj.user.avatar.url if obj.user.avatar else None
        }

class ClapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'claps']


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False, default=serializers.CurrentUserDefault())
    thumbnail = serializers.ImageField(required=False)
    status = serializers.BooleanField(required=True)
    topic_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.filter(is_active=True), many=True, write_only=True, required=True
    )
    topics = TopicSerializer(many=True, read_only=True)
    claps = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        many=True,
        required=False
    )

    def validate_status(self, value):
        return 'publish' if value else 'draft'

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'status', 'content', 'thumbnail', 'topic_ids', 'summary', 'created_at', 'updated_at', 'topics', 'claps']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        topic_ids = validated_data.pop('topic_ids', [])
        claps = validated_data.pop('claps', [])
        author = validated_data.pop('author', None)

        article = Article.objects.create(author=author, **validated_data)
        article.topics.set(topic_ids)
        article.claps.set(claps)
        return article

class TopicFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicFollow
        fields = ['user', 'topic']

    def create(self, validated_data):
        user = self.context['request'].user
        topic = validated_data['topic']
        follow, created = TopicFollow.objects.get_or_create(user=user, topic=topic)
        return follow

class CommentSerializer(serializers.ModelSerializer):
    article = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'parent', 'created_at', 'article']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ArticleDetailCommentsSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True, source='article_comments')

    class Meta:
        model = Article
        fields = ['id', 'title', 'comments']
