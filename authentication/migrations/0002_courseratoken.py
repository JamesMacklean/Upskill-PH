# Generated by Django 4.0.7 on 2023-10-03 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseraToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(choices=[('initial_code', 'Initial Code'), ('access_token', 'Access Token'), ('refresh_token', 'Refresh Token')], max_length=15, unique=True)),
                ('value', models.TextField()),
            ],
        ),
    ]