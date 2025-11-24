from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, UserProfile, Message


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image'] # Поля, которые будут в форме
        # Можно настроить виджеты, лейблы и т.д.
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
            'image': 'Изображение (опционально)',
        }

# Форма для комментариев
class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False) # Скрытое поле для ID родительского комментария

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Напишите комментарий...'}),
        }
        labels = {
            'content': '',
        }

    def __init__(self, *args, **kwargs):
        # Извлекаем post_id из kwargs, если он есть
        self.post_id = kwargs.pop('post_id', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # Убедимся, что post_id был передан
        if not self.post_id:
            raise ValueError("post_id must be provided to CommentForm")

        comment = super().save(commit=False)
        # Привязываем к посту через post_id
        comment.post_id = self.post_id # Используем post_id, а не объект, чтобы избежать лишнего запроса
        if self.cleaned_data.get('parent_id'):
            # Если parent_id есть, находим родительский комментарий
            parent_id = self.cleaned_data['parent_id']
            try:
                comment.parent = Comment.objects.get(id=parent_id, post_id=self.post_id) # Убедимся, что родитель принадлежит этому посту
            except Comment.DoesNotExist:
                # Если родитель не найден, просто сохраняем как комментарий верхнего уровня
                comment.parent = None
        # Если parent_id нет или родитель не найден, parent останется None (комментарий верхнего уровня)

        if commit:
            comment.save()
        return comment

# Новая форма для профиля
class UserProfileForm(forms.ModelForm):
    # Поля из User
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['avatar', 'birth_date', 'first_name', 'last_name', 'bio']

    def __init__(self, *args, **kwargs):
        # Извлекаем user из kwargs, если он есть
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Заполняем поля User формы текущими значениями
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        user = user_profile.user # Получаем связанный User

        # Обновляем поля User
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user_profile.save()
        return user_profile

# форма для личного сообщения
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тема сообщения'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Текст сообщения...'}),
        }
        labels = {
            'subject': 'Тема (опционально)',
            'content': 'Сообщение',
        }