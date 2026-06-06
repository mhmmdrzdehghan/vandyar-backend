from django.urls import path , include
from .views import Register , UpdateProfileView , CustomObtainAuthToken , ProfileDetailView , UsersView

urlpatterns = [
    path('register/', Register.as_view()),
    path('users/', UsersView.as_view()),
    path('profile/', UpdateProfileView.as_view()),
    path('login/', CustomObtainAuthToken.as_view()),
    path('me/', ProfileDetailView.as_view()),
]
