from django.urls import path
from . import views

app_name = 'my_app'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('detail/<int:item_id>/', views.detail_view, name='detail'),
]
