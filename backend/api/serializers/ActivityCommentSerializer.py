from rest_framework import serializers
from api.models import User
from api.models import ActivityComment, Activity

class UserCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name') 

class SpecificActivityCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('id', 'title', 'user')
class CommentCreateSerializer(serializers.ModelSerializer):
    # activity = ActivityCommentSerializer()
    # user = UserCommentSerializer()  # Serialize the user field

    class Meta:
        model = ActivityComment
        fields = ('id', 'activity_id', 'user_id', 'comment', 'date_created')  
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        activity_id = validated_data.pop('activity_id', None)

        if not user_id:
            raise serializers.ValidationError({'error': 'User ID not provided'})
        if not activity_id:
            raise serializers.ValidationError({'error': 'Activity ID not provided'})

        try:
            user = User.objects.get(pk=user_id)
            activity = Activity.objects.get(pk=activity_id)

            # Create the ActivityComment instance using the actual instances
            comment = ActivityComment.objects.create(user_id=user, activity_id=activity, **validated_data)

            return comment
        except User.DoesNotExist:
            raise serializers.ValidationError({'error': 'User not found'})
        except Activity.DoesNotExist:
            raise serializers.ValidationError({'error': 'Activity not found'})


class ActivityCommentSerializer(serializers.ModelSerializer):
    # activity = SpecificActivityCommentSerializer()
    # user = UserCommentSerializer()
    activity = serializers.SerializerMethodField()

    class Meta:
        model = ActivityComment
        fields = ('id', 'comment', 'date_created', 'activity_id', 'user_id', 'activity')
    def get_activity(self, obj):
        activity_data = {
            'id': obj.activity_id.id,
            'title': obj.activity_id.title,
            'description': obj.activity_id.description
        }
        return activity_data
    
    
class ActivityCommentWithUserSerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = ActivityComment
        fields = ('id', 'comment', 'date_created', 'activity', 'user')

    def get_activity(self, obj):
        activity_data = {
            'id': obj.activity_id.id,
            'title': obj.activity_id.title
        }
        return activity_data

    def get_user(self, obj):
        user_data = {
            'id': obj.user_id.id,
            'email': obj.user_id.email,
            'first_name': obj.user_id.first_name,
            'last_name': obj.user_id.last_name
        }
        return user_data