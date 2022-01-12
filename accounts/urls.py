from django.urls import path

from .views import SignupView, CustomLoginView

app_name = 'accounts'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
]