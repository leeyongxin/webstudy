# Generated by Django 2.2.1 on 2019-05-31 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wind', '0004_promise'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
            ],
        ),
        migrations.DeleteModel(
            name='Promise',
        ),
    ]
