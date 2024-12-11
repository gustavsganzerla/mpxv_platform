from django.urls import path
from . import views


app_name = 'my_app'

urlpatterns = [
    path("home/", views.home, name = "home"),
    path("db_home/", views.db_home, name = "db_home"),
    path("view_genome_db/<str:genome_id>", views.view_genome_db, name = "view_genome_db"),
    path("download_query_csv/", views.download_query_csv, name = "download_query_csv"),
    path("download_genome/<str:genome_id>", views.download_genome, name = "download_genome"),
    path("annotation/", views.annotation, name = "annotation")
    
]
