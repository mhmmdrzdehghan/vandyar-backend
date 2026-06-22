from django.shortcuts import render
from rest_framework.generics import CreateAPIView , UpdateAPIView , RetrieveAPIView , ListCreateAPIView
from .serializer import UserSerializer , CustomAuthTokenSerializer , ProfileSerializer
from django.db import transaction
from .models import User , Profile
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
 
class Register(CreateAPIView):
    serializer_class = UserSerializer
     
class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        profile = getattr(user, "Profile", None)

        avatar_url = None
        if profile and profile.avatar:
            avatar_url = request.build_absolute_uri(profile.avatar.url)

        user_data = {
            'id': user.id,
            'role': user.role,
            'username': user.username,
            'phone': profile.phone if profile else None,
            'first_name': profile.first_name if profile else None,
            'last_name': profile.last_name if profile else None,
            'avatar': avatar_url
        }

        return Response({
            'token': token.key,
            'user': user_data
        })
    
class UpdateProfileView(UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.Profile
    
    # def update(self, request, *args, **kwargs):
    #     super().update(request, *args, **kwargs)

    #     return Respo

    

class ProfileDetailView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.Profile
    
    
class UsersView(ListCreateAPIView):
    serializer_class = UserSerializer

    queryset = User.objects.all()


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


