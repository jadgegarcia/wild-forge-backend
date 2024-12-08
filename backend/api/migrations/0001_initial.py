# Generated by Django 4.2.4 on 2024-12-08 14:26

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('role', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Admin'), (1, 'Moderator'), (2, 'Basic')], null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=100)),
                ('description', models.TextField(default='', max_length=10000)),
                ('instruction', models.TextField(default='', max_length=10000)),
                ('submission_status', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('evaluation', models.IntegerField(null=True)),
                ('total_score', models.IntegerField(default=100)),
                ('return_status', models.BooleanField(default=False)),
                ('submission_attempts', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityCriteria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityGeminiSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.TextField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=10000)),
                ('instructions', models.TextField(max_length=10000)),
            ],
        ),
        migrations.CreateModel(
            name='ClassMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Teacher'), (1, 'Student')], null=True)),
                ('status', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'pending'), (1, 'accepted')], null=True)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClassRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_code', models.CharField(max_length=8, unique=True)),
                ('course_name', models.CharField(max_length=100)),
                ('sections', models.CharField(max_length=100)),
                ('schedule', models.CharField(max_length=100)),
                ('max_teams_members', models.IntegerField(default=5)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('invited_users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClassRoomPE',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classroom')),
            ],
        ),
        migrations.CreateModel(
            name='Criteria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('teacher_weight_score', models.DecimalField(decimal_places=2, default=1, max_digits=3)),
                ('student_weight_score', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('video', models.CharField(blank=True, max_length=50, null=True)),
                ('token', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('classroom_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classroom')),
            ],
        ),
        migrations.CreateModel(
            name='MeetingCriteria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.DecimalField(decimal_places=2, max_digits=3)),
                ('criteria_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.criteria')),
                ('meeting_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.meeting')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('system', 'System'), ('assistant', 'Assistant'), ('user', 'User')], max_length=20)),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PeerEval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('forms_link', models.TextField(blank=True, null=True)),
                ('sheet_link', models.TextField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pitch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpringBoardTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, unique=True)),
                ('content', models.TextField()),
                ('rules', models.TextField()),
                ('description', models.TextField()),
                ('date_created', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpringProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(default='')),
                ('is_active', models.BooleanField(default=False)),
                ('score', models.FloatField(default=0)),
                ('reason', models.TextField(default='')),
                ('date_created', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'open'), (0, 'closed')], null=True)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Leader'), (1, 'Member')], null=True)),
                ('status', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'pending'), (1, 'accepted')], null=True)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('class_member_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classmember')),
                ('team_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.team')),
            ],
        ),
        migrations.CreateModel(
            name='SpringProjectBoard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board_id', models.IntegerField(default=0)),
                ('title', models.CharField(max_length=50)),
                ('template_id', models.IntegerField(default=0)),
                ('feedback', models.TextField(default='')),
                ('recommendation', models.TextField(default='')),
                ('references', models.TextField(default='')),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('criteria_feedback', models.TextField(default='')),
                ('score', models.IntegerField(default=0)),
                ('activity_id', models.IntegerField(default=0)),
                ('project_id', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.springproject')),
            ],
        ),
        migrations.AddField(
            model_name='springproject',
            name='team_id',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wildforge_api.team'),
        ),
        migrations.CreateModel(
            name='Remark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remark', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('classmember_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classmember')),
                ('meeting_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.meeting')),
                ('pitch_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.pitch')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.DecimalField(decimal_places=2, max_digits=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('classmember_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classmember')),
                ('meeting_criteria_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.meetingcriteria')),
                ('meeting_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.meeting')),
                ('pitch_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.pitch')),
            ],
        ),
        migrations.AddField(
            model_name='pitch',
            name='team_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.team'),
        ),
        migrations.CreateModel(
            name='MeetingPresentor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_rate_open', models.BooleanField(default=False)),
                ('meeting_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.meeting')),
                ('pitch_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.pitch')),
                ('team_id', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.team')),
            ],
        ),
        migrations.CreateModel(
            name='MeetingComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('classmember_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classmember')),
            ],
        ),
        migrations.AddField(
            model_name='meeting',
            name='comments',
            field=models.ManyToManyField(blank=True, to='wildforge_api.meetingcomment'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='criterias',
            field=models.ManyToManyField(blank=True, to='wildforge_api.meetingcriteria'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='invited_users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='meeting',
            name='owner_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classmember'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='presentors',
            field=models.ManyToManyField(blank=True, to='wildforge_api.meetingpresentor'),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('meeting_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.meeting')),
                ('pitch_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.pitch')),
            ],
        ),
        migrations.CreateModel(
            name='ClassRoomPETaker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveIntegerField(choices=[(0, 'Pending'), (1, 'Completed')], default=0)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('class_member_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classmember')),
                ('class_room_pe_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classroompe')),
            ],
        ),
        migrations.AddField(
            model_name='classroompe',
            name='peer_eval_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.peereval'),
        ),
        migrations.AddField(
            model_name='classmember',
            name='class_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classroom'),
        ),
        migrations.AddField(
            model_name='classmember',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Chatbot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('messages', models.ManyToManyField(to='wildforge_api.message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityWorkAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(max_length=100)),
                ('file_attachment', models.FileField(blank=True, upload_to='activity_work_submissions/')),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('activity_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.activity')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityCriteriaRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strictness', models.IntegerField()),
                ('rating', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('activity_criteria_status', models.IntegerField(default=0)),
                ('activity_criteria_feedback', models.CharField(blank=True, default='', max_length=8000, null=True)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.activity')),
                ('activity_criteria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.activitycriteria')),
            ],
            options={
                'unique_together': {('activity', 'activity_criteria')},
            },
        ),
        migrations.CreateModel(
            name='ActivityComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(max_length=10000)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('activity_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.activity')),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='activityCriteria_id',
            field=models.ManyToManyField(null=True, through='wildforge_api.ActivityCriteriaRelation', to='wildforge_api.activitycriteria'),
        ),
        migrations.AddField(
            model_name='activity',
            name='classroom_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.classroom'),
        ),
        migrations.AddField(
            model_name='activity',
            name='spring_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wildforge_api.springproject'),
        ),
        migrations.AddField(
            model_name='activity',
            name='team_id',
            field=models.ManyToManyField(null=True, to='wildforge_api.team'),
        ),
    ]
