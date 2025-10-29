from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import UserRegisterForm, UserLoginForm, PostForm
from .models import Post, Like
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

@login_required
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
    # Проверяем, поставил ли текущий пользователь лайк
    user_liked = False
    if request.user.is_authenticated:
        user_liked = post.likes.filter(user=request.user).exists()  # Используем связь через related_name='likes'

    # Можно передать дополнительные данные, например, комментарии
    return render(request, 'app/post_detail.html', {
        'post': post,
        'user_liked': user_liked,  # Передаём флаг в шаблон
    })
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

@login_required
def post_delete(request, post_id):
    # Получаем пост или возвращаем 404
    post = get_object_or_404(Post, id=post_id)
    # Проверяем, является ли текущий пользователь автором поста
    if post.author != request.user:
        # Или перенаправляем на главную с сообщением об ошибке
        messages.error(request, 'У вас нет прав для удаления этого поста.')
        return redirect('home')

    if request.method == 'POST':
        # Если это POST-запрос (пользователь подтвердил удаление через модальное окно)
        post_title = post.title # Сохраняем заголовок для сообщения
        post.delete() # Удаляем пост из БД (и связанные объекты, если настроено CASCADE)
        messages.success(request, f'Пост "{post_title}" успешно удалён.')
        return redirect('home') # Перенаправляем на главную страницу

    # Если это GET-запрос (например, прямой доступ по URL),
    # можно перенаправить или показать страницу подтверждения.
    # Обычно для удаления используется POST, но на всякий случай.
    # Лучше перенаправить на детали поста или на главную.
    messages.warning(request, 'Для удаления поста используйте кнопку на странице поста.')
    return redirect('post_detail', post_id=post.id)

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Получаем или создаём объект Like
    # get_or_create возвращает кортеж (объект, создан ли он)
    like_obj, created = Like.objects.get_or_create(user=request.user, post=post)

    if created:
        # Лайк был добавлен
        action = 'liked'
    else:
        # Лайк уже существовал, значит дизлайкаем
        like_obj.delete()
        action = 'unliked'

    # Сообщение
    messages.info(request, f'Вы {action} пост "{post.title}".')

    # Перенаправляем обратно на страницу поста
    # request.META.get('HTTP_REFERER') возвращает предыдущую страницу
    next_url = request.META.get('HTTP_REFERER', reverse('home')) # Если реферера нет, идём на главную
    return HttpResponseRedirect(next_url)