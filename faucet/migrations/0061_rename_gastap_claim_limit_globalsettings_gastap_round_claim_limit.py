# Generated by Django 4.0.4 on 2023-10-24 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0060_rename_weekly_chain_claim_limit_globalsettings_gastap_claim_limit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='globalsettings',
            old_name='gastap_claim_limit',
            new_name='gastap_round_claim_limit',
        ),
    ]
