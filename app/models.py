from django.db import models
from django.contrib.auth.models import User
import os


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)  # blank=True позволяет не заполнять поле

    def __str__(self):
        return self.title

    def get_like_count(self):
        """Возвращает количество лайков для поста."""
        return self.likes.count()

    def user_liked(self, user):
        """Проверяет, поставил ли конкретный пользователь лайк."""
        return self.likes.filter(user=user).exists()

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    # Два нижних метода по желанию
    # Переопределяем метод delete() для удаления файла
    def delete(self, *args, **kwargs):
        # Если есть изображение и оно существует на диске
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)  # Удаляем файл с диска
        super().delete(*args, **kwargs)  # Вызываем родительский delete() для удаления из БД

    # Переопределяем метод save() для удаления старого файла при обновлении
    def save(self, *args, **kwargs):
        # Если объект уже существует в базе данных (то есть редактируется)
        if self.pk:  # pk — первичный ключ, если он есть — объект уже сохранён
            old_post = Post.objects.get(pk=self.pk)
            # Если поле image изменилось (новый файл загружен)
            if old_post.image and old_post.image != self.image:
                # Удаляем старый файл
                if os.path.isfile(old_post.image.path):
                    os.remove(old_post.image.path)
        # Сохраняем объект
        super().save(*args, **kwargs)


# Модель для лайков
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post') # Один пользователь может лайкнуть пост только один раз
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"
