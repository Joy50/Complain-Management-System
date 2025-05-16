from django.urls import path
from .views import *

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('complaints/', ComplainListView.as_view(), name='complain_list'),
    path('complaints/<int:pk>/', ComplainDetailView.as_view(), name='complain_detail'),
    path('complaints/new/', ComplainCreateView.as_view(), name='complain_create'),
    path('complaints/<int:pk>/update/', ComplainUpdateView.as_view(), name='complain_update'),
    path('analytics/', analytics_view, name='analytics'),
    path('chatbot/', chatbot_response, name='chatbot'),
    path('download/<int:pk>/', download_document, name='download_document'),
]