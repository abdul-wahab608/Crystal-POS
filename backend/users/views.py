from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer
from users.permissions import IsAdminUser

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'message': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = None
    try:
        u = User.objects.get(username=username)
        if u.check_password(password) and u.is_active:
            user = u
    except User.DoesNotExist:
        user = None

    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_superuser': user.is_superuser
            }
        })
    else:
        return Response(
            {'message': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'is_superuser': user.is_superuser
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # In a real implementation, you might want to blacklist the token
    return Response({'message': 'Logged out successfully'}) 