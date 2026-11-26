from rest_framework import serializers
from .models import Post,Users
from rest_framework.exceptions import ValidationError

class PostSerializer(serializers.ModelSerializer):
    user = serializers.CharField() 
    class Meta:
        model = Post
        fields = ['id','user','content','image','created_at']
    def create(self, validated_data):
        username = validated_data.pop('user')   # "din"
        try:
            user = Users.objects.get(username=username)  # User object to ids
        except:
            raise ValidationError({"user": "User not found"})
        return Post.objects.create(user=user, **validated_data)