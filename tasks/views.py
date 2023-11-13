from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

''''La clase UserCreationForm de Django es una clase de formulario predefinida que proporciona funcionalidades para la creación de usuarios. '''

# Create your views here.


def home(request):
    # Renderiza el archivo sign_up.html y devuelve la respuesta
    return render(request, 'home.html')

# función que permite crear un usuario


def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            # cargar datos que se van a usar en la vista
            'form': UserCreationForm
        })

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                # registrar usuario
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                # crear session de usuario
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'User already exists'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Password do not match'
        })


@login_required
def tasks(request):
    # filtrar tareas por usuario
    # datecompleted__isnull=True mostrar tareas que no se han completado
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def tasks_completed(request):
    # filtrar tareas por usuario
    # datecompleted__isnull=True mostrar tareas que no se han completado
    tasks = Task.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            # crea una instancia de un formulario llamado TaskForm.
            form = TaskForm(request.POST)
            # El parámetro commit=False significa que los datos no se guardan inmediatamente en la base de datos
            new_task = form.save(commit=False)
            # establece el campo de usuario de la nueva instancia de tarea con el usuario actual que realiza la solicitud.
            new_task.user = request.user
            # guarda la instancia de la tarea en la base de datos
            new_task.save()
            return redirect('tasks')

        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Please provide validate data'
            })


@login_required
def task_detail(request, task_id):
    if request.method == 'GET':

        # buscar una tarea por el parametro task_id
        # sino encuentra el objeto envia una vista de error 404
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            # editar tarea
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error updating task'})


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
# función que permite hacer logout de nuestra sesión


@login_required
def signout(request):
    logout(request)
    return redirect('home')

# función que permite autenticarnos al sistema


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            # enviar un formulario de autentificación a la vista signin
            'form': AuthenticationForm
        })
    else:

        # función para autenticar
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        # si el usuario no existe entonces
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            # guardamos la sesión del usuario en caso de que si exista
            login(request, user)
            # redirigimos a la vista tasks
            return redirect('tasks')
