# Generated by Django 4.0.4 on 2024-03-10 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tokenTap', '0039_tokendistribution_is_one_time_claim'),
    ]

    operations = [
        migrations.AlterField(
            model_name='constraint',
            name='name',
            field=models.CharField(choices=[('core.BrightIDMeetVerification', 'BrightIDMeetVerification'), ('core.BrightIDAuraVerification', 'BrightIDAuraVerification'), ('core.HasNFTVerification', 'HasNFTVerification'), ('core.HasTokenVerification', 'HasTokenVerification'), ('core.AllowListVerification', 'AllowListVerification'), ('core.HasENSVerification', 'HasENSVerification'), ('core.HasLensProfile', 'HasLensProfile'), ('core.IsFollowingLensUser', 'IsFollowingLensUser'), ('core.BeFollowedByLensUser', 'BeFollowedByLensUser'), ('core.DidMirrorOnLensPublication', 'DidMirrorOnLensPublication'), ('core.DidCollectLensPublication', 'DidCollectLensPublication'), ('core.HasMinimumLensPost', 'HasMinimumLensPost'), ('core.HasMinimumLensFollower', 'HasMinimumLensFollower'), ('core.BeFollowedByFarcasterUser', 'BeFollowedByFarcasterUser'), ('core.HasMinimumFarcasterFollower', 'HasMinimumFarcasterFollower'), ('core.DidLikedFarcasterCast', 'DidLikedFarcasterCast'), ('core.DidRecastFarcasterCast', 'DidRecastFarcasterCast'), ('core.IsFollowingFarcasterUser', 'IsFollowingFarcasterUser'), ('core.HasFarcasterProfile', 'HasFarcasterProfile'), ('tokenTap.OncePerMonthVerification', 'OncePerMonthVerification'), ('tokenTap.OnceInALifeTimeVerification', 'OnceInALifeTimeVerification'), ('faucet.OptimismHasClaimedGasInThisRound', 'OptimismHasClaimedGasInThisRound')], max_length=255, unique=True),
        ),
    ]
