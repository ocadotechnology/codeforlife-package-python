# Generated by Django 3.2.18 on 2023-03-03 10:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AimmoCharacter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image_path', models.CharField(max_length=255)),
                ('sort_order', models.IntegerField()),
                ('alt', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('access_code', models.CharField(max_length=5, null=True)),
                ('classmates_data_viewable', models.BooleanField(default=False)),
                ('always_accept_requests', models.BooleanField(default=False)),
                ('accept_requests_until', models.DateTimeField(null=True)),
                ('creation_time', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'classes',
            },
        ),
        migrations.CreateModel(
            name='DailyActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('csv_click_count', models.PositiveIntegerField(default=0)),
                ('login_cards_click_count', models.PositiveIntegerField(default=0)),
                ('primary_coding_club_downloads', models.PositiveIntegerField(default=0)),
                ('python_coding_club_downloads', models.PositiveIntegerField(default=0)),
                ('level_control_submits', models.PositiveBigIntegerField(default=0)),
                ('teacher_lockout_resets', models.PositiveIntegerField(default=0)),
                ('indy_lockout_resets', models.PositiveIntegerField(default=0)),
                ('school_student_lockout_resets', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Daily activities',
            },
        ),
        migrations.CreateModel(
            name='DynamicElement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=64, unique=True)),
                ('active', models.BooleanField(default=False)),
                ('text', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('postcode', models.CharField(max_length=10, null=True)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('creation_time', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('login_type', models.CharField(max_length=100, null=True)),
                ('class_field', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.class')),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.school')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('developer', models.BooleanField(default=False)),
                ('awaiting_email_verification', models.BooleanField(default=False)),
                ('aimmo_badges', models.CharField(blank=True, max_length=200, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False)),
                ('blocked_time', models.DateTimeField(blank=True, null=True)),
                ('invited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invited_teachers', to='common.teacher')),
                ('new_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='new_teacher', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teacher_school', to='common.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='common.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_id', models.CharField(max_length=64, null=True)),
                ('blocked_time', models.DateTimeField(blank=True, null=True)),
                ('class_field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='common.class')),
                ('new_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='new_student', to=settings.AUTH_USER_MODEL)),
                ('pending_class_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_request', to='common.class')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='common.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolTeacherInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=32)),
                ('invited_teacher_first_name', models.CharField(max_length=150)),
                ('invited_teacher_last_name', models.CharField(max_length=150)),
                ('invited_teacher_email', models.EmailField(max_length=254)),
                ('invited_teacher_is_admin', models.BooleanField(default=False)),
                ('expiry', models.DateTimeField()),
                ('creation_time', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('from_teacher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='school_invitations', to='common.teacher')),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teacher_invitations', to='common.school')),
            ],
        ),
        migrations.CreateModel(
            name='JoinReleaseStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(max_length=64)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student', to='common.student')),
            ],
        ),
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=30)),
                ('email', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('expiry', models.DateTimeField()),
                ('verified', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_verifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='class',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_classes', to='common.teacher'),
        ),
        migrations.AddField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_teacher', to='common.teacher'),
        ),
    ]