from django.db import models
from blog.models import Post

# Create your models here.

class Comment(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, 'normal'),
        (STATUS_DELETE, 'delete'),
            )

    target = models.ForeignKey(Post, verbose_name='comment target', on_delete=models.CASCADE)
    content = models.CharField(max_length=200, verbose_name='content')
    nickname = models.CharField(max_length=50, verbose_name='nickname')
    website = models.URLField(verbose_name='wesite')
    email = models.EmailField(verbose_name='email')

    status = models.PositiveIntegerField(default=STATUS_NORMAL,
                                         choices=STATUS_ITEMS,
                                         verbose_name='status')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')

    class Meta:
        verbose_name = verbose_name_plural = 'comment'
