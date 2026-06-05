from django.shortcuts import render
from rest_framework.generics import CreateAPIView , UpdateAPIView , RetrieveAPIView
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
        serializer = self.serializer_class(data=request.data , context={'request':request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token , created = Token.objects.get_or_create(user=user)
        user_data = {'id':user.id,  'role':user.role , 'username':user.username ,
                    'phone':user.Profile.phone , 'first_name':user.Profile.first_name, 
                    'last_name':user.Profile.last_name , 'avatar':user.Profile.avatar  if user.Profile.avatar else None}

        return Response({'token':token.key , 'user':user_data})
    
class UpdateProfileView(UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.Profile
    

class ProfileDetailView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.Profile
    
    