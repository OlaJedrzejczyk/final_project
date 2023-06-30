from django.urls import path
from . import views
from .views import HomeView, GenreFormView, ResultView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('form/', GenreFormView.as_view(), name='form'),
    path('result', ResultView.as_view(), name='result'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),
]