# Generated by Django 2.2 on 2019-04-26 05:29

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
            name='SideBar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='tile')),
                ('display_type', models.PositiveIntegerField(choices=[(1, 'HTML'), (2, 'new article'), (3, 'hot article'), (4, 'new comments')], default=1, verbose_name='display type')),
                ('content', models.CharField(blank=True, help_text='can be blank if not HTML type', max_length=500, verbose_name='content')),
                ('status', models.PositiveIntegerField(choices=[(1, 'show'), (0, 'hide')], default=1, verbose_name='status')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='create_time')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author')),
            ],
            options={
                'verbose_name': 'side bar',
                'verbose_name_plural': 'side bar',
            },
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='tile')),
                ('href', models.URLField(verbose_name='link')),
                ('status', models.PositiveIntegerField(choices=[(1, 'normal'), (0, 'delete')], default=1, verbose_name='status')),
                ('weight', models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=1, help_text='weight desend order', verbose_name='weight')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='create_time')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author')),
            ],
            options={
                'verbose_name': 'link',
                'verbose_name_plural': 'link',
            },
        ),
    ]
