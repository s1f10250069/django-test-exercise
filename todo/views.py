from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseNotAllowed
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task


# Create your views here.
def index(request):
    if request.method == 'POST':

        due_at_raw = request.POST.get('due_at')
        due_at_parsed = parse_datetime(due_at_raw) if due_at_raw else None
        task = Task(
            title=request.POST['title'],
            due_at=make_aware(due_at_parsed) if due_at_parsed else None)
        task.save()

    keyword = request.GET.get('keyword')

    if keyword:
        tasks = Task.objects.filter(title__icontains=keyword)
    elif request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at')

    remaining_tasks_count = Task.objects.filter(completed=False).count()

    context = {
        'tasks': tasks,
        'remaining_tasks_count': remaining_tasks_count,
    }

    return render(request, 'todo/index.html', context)


def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    
    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html', context)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
            raise Http404("Task does not exist")
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))
        task.save()
        return redirect(detail, task_id)

    context = {
        'task': task
    }
    return render(request, "todo/edit.html", context)


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)


def complete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    task.completed = True
    task.save()
    return redirect(index)


def close(request, task_id):
    try:
        Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    return redirect(index)
