from rest_framework import serializers

from api.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'role']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'password': 'Password',
            'role': 'Role',
            'is_superuser': 'Is Superuser'
        }

        # set default values
        extra_kwargs = {
            'role': {'default': User.BASIC, 'required': False},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)
    
class SuperUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role', 'is_superuser']
        # make all read-only fields
        extra_kwargs = {
            'first_name': {'read_only': True, 'required': False},
            'last_name': {'read_only': True, 'required': False},
            'email': {'read_only': True, 'required': False},
            'role': {'read_only': True, 'required': False},
            'is_superuser': {'read_only': True, 'required': False}
        }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField(max_length=50, write_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if not email:
            raise serializers.ValidationError('An email address is required to log in.')

        if not password:
            raise serializers.ValidationError('A password is required to log in.')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('A user with this email and password was not found.')

        if not user.check_password(password):
            raise serializers.ValidationError('A user with this email and password was not found.')

        serializer_data = UserSerializer(user).data
        return serializer_data