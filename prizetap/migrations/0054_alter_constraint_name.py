# Generated by Django 4.0.4 on 2024-02-28 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prizetap', '0053_alter_constraint_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='constraint',
            name='name',
            field=models.CharField(choices=[('core.BrightIDMeetVerification', 'BrightIDMeetVerification'), ('core.BrightIDAuraVerification', 'BrightIDAuraVerification'), ('core.HasNFTVerification', 'HasNFTVerification'), ('core.HasTokenVerification', 'HasTokenVerification'), ('core.AllowListVerification', 'AllowListVerification'), ('core.HasENSVerification', 'HasENSVerification'), ('core.HasLensProfile', 'HasLensProfile'), ('core.IsFollowingLensUser', 'IsFollowingLensUser'), ('core.BeFollowedByLensUser', 'BeFollowedByLensUser'), ('core.DidMirrorOnLensPublication', 'DidMirrorOnLensPublication'), ('core.DidCollectLensPublication', 'DidCollectLensPublication'), ('core.HasMinimumLensPost', 'HasMinimumLensPost'), ('core.HasMinimumLensFollower', 'HasMinimumLensFollower'), ('prizetap.HaveUnitapPass', 'HaveUnitapPass'), ('prizetap.NotHaveUnitapPass', 'NotHaveUnitapPass'), ('faucet.OptimismDonationConstraint', 'OptimismDonationConstraint'), ('faucet.OptimismClaimingGasConstraint', 'OptimismClaimingGasConstraint')], max_length=255, unique=True),
        ),
    ]
