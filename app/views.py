from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserLoginForm, PostForm
from .models import Post
# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Аккаунт {username} успешно создан")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, "app/register.html", {'form': form})
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Неправильное имя пользователя или пароль!")

    else:
        form = UserLoginForm()
    return render(request, 'app/login.html', {'form': form})
def user_logout(request):
    logout(request)
    return redirect('login')
def home(request):
    # Получаем все объекты Post из базы данных
    posts = Post.objects.all()

    # Передаем список posts в шаблон home.html через контекст
    context = {
        'posts': posts, # 'posts' - это имя переменной, которое будет доступно в шаблоне
    }
    return render(request, 'app/home.html', context)
@login_required
def post_detail(request, post_id):
    # Получаем конкретный пост по ID или возвращаем 404, если не найден
    post = get_object_or_404(Post, id=post_id)
    # Можно передать дополнительные данные, например, комментарии
    return render(request, 'app/post_detail.html', {'post': post})
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST) # Предполагается, что у тебя есть PostForm
        if form.is_valid():
            post = form.save(commit=False) # Не сохраняем в базу пока
            post.author = request.user # Присваиваем автора текущему пользователю
            post.save() # Теперь сохраняем
            messages.success(request, 'Пост успешно создан!')
            return redirect('home') # Перенаправляем на главную страницу после создания
    else:
        form = PostForm()

    return render(request, 'app/post_create.html', {'form': form})