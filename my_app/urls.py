from django.urls import path
from . import views


app_name = 'my_app'

urlpatterns = [
    path("home/", views.home, name = "home"),
    path("db_home/", views.db_home, name = "db_home"),
    path("view_genome_db/<str:genome_id>", views.view_genome_db, name = "view_genome_db")
    
]
