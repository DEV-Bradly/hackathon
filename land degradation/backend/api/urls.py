from django.urls import path
from . import views

urlpatterns = [
    path("user", views.current_user, name="current_user"),
    path("analyze", views.analyze_land_issue, name="analyze_land_issue"),
    path("agromet", views.agromet_snapshot, name="agromet_snapshot"),
    path("projects", views.projects, name="projects"),
]
