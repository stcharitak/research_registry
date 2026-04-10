from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["id"] = user.id
        token["username"] = user.username
        token["first_name"] = user.first_name if user.first_name else None
        token["last_name"] = user.last_name if user.last_name else None
        token["email"] = user.email if user.email else None
        token["role"] = user.role.name if user.role else None
        return token
