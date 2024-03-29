# Generated by Django 4.0.4 on 2024-01-23 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tokenTap', '0032_alter_constraint_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.CharField(max_length=255, unique=True)),
                ('value', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='constraint',
            name='name',
            field=models.CharField(choices=[('core.BrightIDMeetVerification', 'BrightIDMeetVerification'), ('core.BrightIDAuraVerification', 'BrightIDAuraVerification'), ('core.HasNFTVerification', 'HasNFTVerification'), ('core.HasTokenVerification', 'HasTokenVerification'), ('core.AllowListVerification', 'AllowListVerification'), ('tokenTap.OncePerMonthVerification', 'OncePerMonthVerification'), ('tokenTap.OnceInALifeTimeVerification', 'OnceInALifeTimeVerification'), ('faucet.OptimismHasClaimedGasInThisRound', 'OptimismHasClaimedGasInThisRound')], max_length=255, unique=True),
        ),
    ]
