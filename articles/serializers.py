from rest_framework import serializers
from .models import Article, Topic, TopicFollow, Comment, Clap, Report
from users.models import CustomUser

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'article', 'message', 'created_at', 'read_at']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'is_active']

class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'status', 'content', 'thumbnail', 'topic_ids', 'summary', 'created_at', 'updated_at', 'topics', 'claps']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at'] # ba'zilarni o'qish

class ArticleCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    topics = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), many=True)

    class Meta:
        model = Article
        fields = ['title', 'summary', 'content', 'thumbnail', 'user', 'topics']

    def create(self, validated_data): # yaatish
        return super().create(validated_data)

class ArticleDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    topics = TopicSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'user', 'title', 'summary', 'content', 'status', 'thumbnail', 'topics', 'created_at', 'updated_at']

    def get_user(self, obj): # get information
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
    user = serializers.ReadOnlyField(source='user.username')
    article = serializers.ReadOnlyField(source='article.id')

    class Meta:
        model = Clap
        fields = ['user', 'article', 'count']
        read_only_fields = ['user', 'article'] # ba'zilarni o'qish


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
        read_only_fields = ['id', 'status', 'created_at', 'updated_at'] # ba'zilarni o'qish

    def create(self, validated_data): # article yaratish
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

    def create(self, validated_data): # topic yaratish
        user = self.context['request'].user
        topic = validated_data['topic']
        follow, created = TopicFollow.objects.get_or_create(user=user, topic=topic)
        return follow

class CommentSerializer(serializers.ModelSerializer):
    article = serializers.PrimaryKeyRelatedField(read_only=True) # articleni ulash

    class Meta:
        model = Comment
        fields = ['id', 'content', 'parent', 'created_at', 'article']

    def create(self, validated_data): # comment yaratish
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ArticleDetailCommentsSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True, source='article_comments') # commentni ulash

    class Meta:
        model = Article
        fields = ['id', 'title', 'comments']
