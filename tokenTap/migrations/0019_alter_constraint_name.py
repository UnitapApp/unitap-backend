# Generated by Django 4.0.4 on 2023-10-24 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tokenTap', '0018_constraint_icon_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='constraint',
            name='name',
            field=models.CharField(choices=[('BrightIDMeetVerification', 'BrightIDMeetVerification'), ('BrightIDAuraVerification', 'BrightIDAuraVerification'), ('OncePerWeekVerification', 'OncePerWeekVerification'), ('OncePerMonthVerification', 'OncePerMonthVerification'), ('OnceInALifeTimeVerification', 'OnceInALifeTimeVerification'), ('OptimismHasClaimedGasInThisRound', 'OptimismHasClaimedGasInThisRound')], max_length=255, unique=True),
        ),
    ]
