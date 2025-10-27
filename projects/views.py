import json
from datetime import date
from django.http import JsonResponse, HttpRequest, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from .models import Project, Task
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def index(request: HttpRequest):
    """Serve the single-page Vue frontend and set CSRF cookie."""
    return render(request, "projects/index.html")


def _parse_json(request: HttpRequest) -> dict:
    """Parse request.body as JSON and return a dict ({} if invalid/empty)."""
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


def _bad_request(message: str) -> JsonResponse:
    """Return a 400 JSON error response with a message."""
    return JsonResponse({"error": message}, status=400)


def projects_collection(request: HttpRequest) -> JsonResponse:
    """
    GET: return list of projects.
    POST: create a new project from JSON body.
    """
    if request.method == "GET":
        items = [p_to_dict(p) for p in Project.objects.all().order_by("-priority", "name")]
        return JsonResponse({"projects": items}, status=200)

    if request.method == "POST":
        payload = _parse_json(request)
        required = ("name", "description", "start_date", "active", "priority")
        if not all(k in payload for k in required):
            return _bad_request("Missing required fields.")

        try:
            project = Project.objects.create(
                name=payload["name"],
                description=payload.get("description", ""),
                start_date=date.fromisoformat(payload["start_date"]),
                active=bool(payload["active"]),
                priority=int(payload["priority"]),
            )
            return JsonResponse({"project": p_to_dict(project)}, status=201)
        except (ValueError, ValidationError) as exc:
            return _bad_request(str(exc))

    return HttpResponseNotAllowed(["GET", "POST"])


def project_resource(request: HttpRequest, project_id: int) -> JsonResponse:
    """
    GET: return a single project including its tasks.
    PUT: update fields of a project.
    DELETE: delete the project.
    """
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "GET":
        data = p_to_dict(project)
        data["tasks"] = [t_to_dict(t) for t in project.tasks.all().order_by("due_date")]
        return JsonResponse({"project": data}, status=200)

    if request.method == "PUT":
        payload = _parse_json(request)
        # optional fields
        if "name" in payload:
            project.name = payload["name"]
        if "description" in payload:
            project.description = payload["description"]
        if "start_date" in payload:
            project.start_date = date.fromisoformat(payload["start_date"])
        if "active" in payload:
            project.active = bool(payload["active"])
        if "priority" in payload:
            project.priority = int(payload["priority"])

        try:
            project.full_clean()
            project.save()
            return JsonResponse({"project": p_to_dict(project)}, status=200)
        except ValidationError as exc:
            return _bad_request(str(exc))

    if request.method == "DELETE":
        project.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["GET", "PUT", "DELETE"])


def project_tasks_collection(request: HttpRequest, project_id: int) -> JsonResponse:
    """
    GET: list tasks under a project.
    POST: create a task under the project.
    """
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "GET":
        tasks = [t_to_dict(t) for t in project.tasks.all().order_by("due_date")]
        return JsonResponse({"tasks": tasks}, status=200)

    if request.method == "POST":
        payload = _parse_json(request)
        required = ("title", "notes", "due_date", "completed", "estimate_hours")
        if not all(k in payload for k in required):
            return _bad_request("Missing required fields.")

        try:
            task = Task.objects.create(
                project=project,
                title=payload["title"],
                notes=payload.get("notes", ""),
                due_date=date.fromisoformat(payload["due_date"]),
                completed=bool(payload["completed"]),
                estimate_hours=int(payload["estimate_hours"]),
            )
            return JsonResponse({"task": t_to_dict(task)}, status=201)
        except (ValueError, ValidationError) as exc:
            return _bad_request(str(exc))

    return HttpResponseNotAllowed(["GET", "POST"])

def task_resource(request: HttpRequest, task_id: int) -> JsonResponse:
    """
    PUT: update a task.
    DELETE: delete a task.
    """
    task = get_object_or_404(Task, pk=task_id)

    if request.method == "PUT":
        payload = _parse_json(request)
        if "title" in payload:
            task.title = payload["title"]
        if "notes" in payload:
            task.notes = payload["notes"]
        if "due_date" in payload:
            task.due_date = date.fromisoformat(payload["due_date"])
        if "completed" in payload:
            task.completed = bool(payload["completed"])
        if "estimate_hours" in payload:
            task.estimate_hours = int(payload["estimate_hours"])

        try:
            task.full_clean()
            task.save()
            return JsonResponse({"task": t_to_dict(task)}, status=200)
        except ValidationError as exc:
            return _bad_request(str(exc))

    if request.method == "DELETE":
        task.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["PUT", "DELETE"])


def p_to_dict(project: Project) -> dict:
    """Serialize a Project to a JSON-safe dict."""
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date.isoformat(),
        "active": project.active,
        "priority": project.priority,
    }


def t_to_dict(task: Task) -> dict:
    """Serialize a Task to a JSON-safe dict."""
    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "notes": task.notes,
        "due_date": task.due_date.isoformat(),
        "completed": task.completed,
        "estimate_hours": task.estimate_hours,
    }
