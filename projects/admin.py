from django.contrib import admin
from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "priority", "active", "start_date")
    list_filter = ("active", "start_date")
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "project", "completed", "due_date", "estimate_hours")
    list_filter = ("completed", "due_date")
    search_fields = ("title", "notes")
