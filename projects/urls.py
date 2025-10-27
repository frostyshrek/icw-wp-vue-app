from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("api/projects/", views.projects_collection, name="projects_collection"),
    path("api/projects/<int:project_id>/", views.project_resource, name="project_resource"),
    path("api/projects/<int:project_id>/tasks/", views.project_tasks_collection, name="project_tasks_collection"),

    path("api/tasks/<int:task_id>/", views.task_resource, name="task_resource"),
]
