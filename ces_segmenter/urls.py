from django.urls import path
from .views import ProcessCSVView

urlpatterns = [
    path('upload/', ProcessCSVView.as_view(), name='upload_csv'),
]