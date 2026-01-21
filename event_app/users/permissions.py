from rest_framework.permissions import BasePermission
from .models import AuthToken

class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return False
        token_key = auth_header.replace('Token ', '')
        try:
            token = AuthToken.objects.get(key=token_key)
            request.user = token.user
            return token.user.is_active
        except AuthToken.DoesNotExist:
            return False
