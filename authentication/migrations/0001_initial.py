# Generated by Django 4.0.7 on 2023-10-03 21:42

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
            name='Partner',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True)),
                ('url', models.URLField(null=True)),
                ('image_url', models.URLField(null=True)),
                ('partner_logo', models.URLField(null=True)),
                ('slug', models.SlugField(null=True)),
                ('course_number', models.PositiveSmallIntegerField(default=0)),
                ('description', models.TextField(blank=True, default='')),
                ('links', models.TextField(blank=True, default='')),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Programs',
            },
        ),
        migrations.CreateModel(
            name='Scholar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('photo_verification', models.URLField()),
                ('status', models.BooleanField(null=True)),
                ('partner_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.partner')),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProgramGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('AB', 'Available Programs'), ('OG', 'On Going')], default='AVAILABLE', max_length=2)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='authentication.program')),
            ],
            options={
                'verbose_name_plural': 'Program Groups',
            },
        ),
        migrations.AddField(
            model_name='program',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='programs', to='authentication.programgroup'),
        ),
        migrations.AddField(
            model_name='program',
            name='partner_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.partner'),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fname', models.CharField(max_length=200, null=True)),
                ('middle_name', models.CharField(max_length=200, null=True)),
                ('lname', models.CharField(max_length=200, null=True)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='')),
                ('about', models.CharField(max_length=500, null=True)),
                ('country', models.CharField(max_length=200, null=True)),
                ('region', models.CharField(max_length=200, null=True)),
                ('province', models.CharField(max_length=200, null=True)),
                ('municipality', models.CharField(max_length=200, null=True)),
                ('gender', models.CharField(max_length=200, null=True)),
                ('birthday', models.DateTimeField(null=True)),
                ('social', models.CharField(max_length=200, null=True)),
                ('phone', models.IntegerField(null=True)),
                ('details_privacy', models.CharField(max_length=200, null=True)),
                ('last_modified', models.DateField(null=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.CreateModel(
            name='PartnerAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True)),
                ('partner_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='partner_admin', to='authentication.partner')),
            ],
        ),
        migrations.CreateModel(
            name='Employment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('employ_status', models.CharField(max_length=255, null=True)),
                ('industry', models.CharField(max_length=255, null=True)),
                ('employer', models.CharField(max_length=255, null=True)),
                ('occupation', models.CharField(max_length=255, null=True)),
                ('experience', models.CharField(max_length=255, null=True)),
                ('last_modified', models.DateTimeField(null=True)),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('degree', models.CharField(max_length=2, null=True)),
                ('school', models.CharField(max_length=200, null=True)),
                ('study', models.CharField(max_length=200, null=True)),
                ('last_modified', models.DateTimeField(null=True)),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('SL', 'Shortlisted'), ('WL', 'Waitlisted'), ('AP', 'Approved'), ('RE', 'Rejected')], default='SL', max_length=2)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='authentication.profile', verbose_name='Scholarium username')),
                ('program', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='authentication.program', verbose_name='Program')),
            ],
            options={
                'verbose_name_plural': 'Scholarship Applications',
            },
        ),
    ]
