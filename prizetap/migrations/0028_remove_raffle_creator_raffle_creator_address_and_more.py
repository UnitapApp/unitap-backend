# Generated by Django 4.0.4 on 2023-09-23 08:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0017_alter_userprofile_username'),
        ('prizetap', '0027_raffle_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='raffle',
            name='creator',
        ),
        migrations.AddField(
            model_name='raffle',
            name='creator_address',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='raffle',
            name='creator_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='raffle',
            name='creator_profile',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='raffles', to='authentication.userprofile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='raffle',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='raffle',
            name='tx_hash',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='raffle',
            name='raffleId',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='raffle',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('REJECTED', 'Rejected'), ('VERIFIED', 'Verified'), ('HELD', 'Held'), ('WS', 'Winner is set')], default='PENDING', max_length=10),
        ),
    ]
