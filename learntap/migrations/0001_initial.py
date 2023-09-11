# Generated by Django 4.0.4 on 2023-09-11 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Constraint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('BrightIDMeetVerification', 'BrightIDMeetVerification'), ('BrightIDAuraVerification', 'BrightIDAuraVerification')], max_length=255, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('VER', 'Verification'), ('TIME', 'Time')], default='VER', max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('response', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('creator_name', models.CharField(blank=True, max_length=200, null=True)),
                ('creator_url', models.URLField(blank=True, null=True)),
                ('discord_url', models.URLField(blank=True, null=True)),
                ('twitter_url', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('imageUrl', models.CharField(blank=True, max_length=200, null=True)),
                ('is_promoted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('constraint_params', models.TextField(blank=True, null=True)),
                ('constraints', models.ManyToManyField(blank=True, related_name='missions', to='learntap.constraint')),
                ('tags', models.ManyToManyField(blank=True, to='learntap.tags')),
            ],
        ),
    ]
