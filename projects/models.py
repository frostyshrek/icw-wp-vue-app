from django.db import models


class Project(models.Model):
    """Main model representing a project that groups many tasks."""

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)

    def __str__(self) -> str:
        """Return a readable representation for admin/debug."""
        return f"{self.name} (priority {self.priority})"


class Task(models.Model):
    """Secondary model representing a task that belongs to a project."""

    project = models.ForeignKey(
        Project, related_name="tasks", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    estimate_hours = models.IntegerField(default=1)

    def __str__(self) -> str:
        """Return a readable representation for admin/debug."""
        return f"{self.title} → Project {self.project_id}"
