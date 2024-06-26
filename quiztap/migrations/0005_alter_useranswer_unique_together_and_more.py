# Generated by Django 4.0.4 on 2024-04-06 08:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0032_gitcoinpassportconnection'),
        ('quiztap', '0004_alter_competition_status'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='useranswer',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='useranswer',
            name='user_competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_answer', to='quiztap.usercompetition'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='useranswer',
            unique_together={('user_competition', 'question')},
        ),
        migrations.AlterUniqueTogether(
            name='usercompetition',
            unique_together={('user_profile', 'competition')},
        ),
        migrations.RemoveField(
            model_name='useranswer',
            name='user_profile',
        ),
    ]
