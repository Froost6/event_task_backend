from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, AuthToken
from .serializers import RegisterSerializer, LoginSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Пользователь зарегистрирован"}, status=201)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=400)

        if not user.check_password(serializer.validated_data['password']):
            return Response({'error': 'Неверный пароль'}, status=400)

        token, _ = AuthToken.objects.get_or_create(user=user, defaults={'key': AuthToken.generate()})
        return Response({"token": token.key})
