
from django.urls import path,re_path,include
from .data_loader.operate_database import db_insert
from .views import load_data,configurate_parameters,execute_strategy,upload_files

urlpatterns = [
    path('db_insert/',db_insert),
    path('configurate_parameters/',configurate_parameters,name="configurate_parameters"),
    path('load_data/',load_data,name="load_data"),
    path('upload_files/',upload_files,name="upload_files"),
    path('execute_strategy/',execute_strategy,name="execute_strategy"),

]