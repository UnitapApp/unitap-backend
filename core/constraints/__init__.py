import importlib

from django.core.exceptions import ImproperlyConfigured

from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.constraints.arbitrum import (
    BridgeEthToArb,
    DelegateArb,
    DidDelegateArbToAddress,
)
from core.constraints.bright_id import (
    BrightIDAuraVerification,
    BrightIDMeetVerification,
)
from core.constraints.captcha import HasVerifiedCloudflareCaptcha
from core.constraints.EAS import Attest, BeAttestedBy
from core.constraints.ens import HasENSVerification
from core.constraints.farcaster import (
    BeFollowedByFarcasterUser,
    DidLikedFarcasterCast,
    DidRecastFarcasterCast,
    HasFarcasterProfile,
    HasMinimumFarcasterFollower,
    IsFollowingFarcasterBatch,
    IsFollowingFarcasterChannel,
    IsFollowingFarcasterUser,
)
from core.constraints.general import (
    AllowListVerification,
    HasNFTVerification,
    HasTokenTransferVerification,
    HasTokenVerification,
)
from core.constraints.gitcoin_passport import (
    HasDonatedOnGitcoin,
    HasGitcoinPassportProfile,
    HasMinimumHumanityScore,
)
from core.constraints.lens import (
    BeFollowedByLensUser,
    DidCollectLensPublication,
    DidMirrorOnLensPublication,
    HasLensProfile,
    HasMinimumLensFollower,
    HasMinimumLensPost,
    IsFollowingLensUser,
)
from core.constraints.muon_node import HasMuonNode
from core.constraints.octant import GLMStakingVerification
from core.constraints.optimism import DelegateOP, DidDelegateOPToAddress
from core.constraints.twitter import (
    BeFollowedByTwitterUser,
    DidQuoteTweet,
    DidRetweetTweet,
    HasCommentOnATweet,
    HasMinimumTweetCount,
    HasMinimumTwitterFollowerCount,
    HasTwitter,
    HasVoteOnATweet,
    IsFollowingTwitterBatch,
    IsFollowinTwitterUser,
)
from core.constraints.zora import DidMintZoraNFT


def get_constraint(constraint_label: str) -> ConstraintVerification:
    app_name, constraint_name = constraint_label.split(".")
    constraints_module_name = f"{app_name}.constraints"
    try:
        constraints_module = importlib.import_module(constraints_module_name)
        constraint_class = getattr(constraints_module, constraint_name)
        return constraint_class
    except (ModuleNotFoundError, AttributeError):
        raise ImproperlyConfigured(
            f"Constraint '{constraint_name}' not found in any app."
        )
