from django.urls import path
from . import views


app_name = 'my_app'

urlpatterns = [
    path("test_view/", views.test_view, name = "test_view")
    
]
