# Generated by Django 2.2.1 on 2019-08-14 01:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('status', models.PositiveIntegerField(choices=[(1, 'normal'), (0, 'delete')], default=1, verbose_name='status')),
                ('is_nav', models.BooleanField(default=False, verbose_name='is navigate')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='create_time')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'category',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='name')),
                ('status', models.PositiveIntegerField(choices=[(1, 'normal'), (0, 'delete')], default=1, verbose_name='status')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='create_time')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author')),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tag',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('desc', models.CharField(blank=True, max_length=1024, verbose_name='description')),
                ('content', models.TextField(help_text='content must be MarkDown format', verbose_name='content')),
                ('status', models.PositiveIntegerField(choices=[(1, 'normal'), (0, 'delete'), (2, 'draft')], default=1, verbose_name='status')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='create_time')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Category', verbose_name='category')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('tag', models.ManyToManyField(to='blog.Tag', verbose_name='tag')),
            ],
            options={
                'verbose_name': 'post',
                'verbose_name_plural': 'post',
                'ordering': ['-id'],
            },
        ),
    ]
