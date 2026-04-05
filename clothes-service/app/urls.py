from django.urls import path
from .views import ClothesListCreate, ClothesDetail

urlpatterns = [
    path('clothes/', ClothesListCreate.as_view()),
    path('clothes/<int:pk>/', ClothesDetail.as_view()),
]