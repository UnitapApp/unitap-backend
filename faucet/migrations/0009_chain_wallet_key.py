# Generated by Django 4.0.4 on 2022-04-16 11:57

from django.db import migrations
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0008_chain_max_claim_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='chain',
            name='wallet_key',
            field=encrypted_model_fields.fields.EncryptedCharField(default=''),
            preserve_default=False,
        ),
    ]
