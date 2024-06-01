import importlib

from django.core.exceptions import ImproperlyConfigured

from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.constraints.arb_bridge import BridgeEthToArb
from core.constraints.bright_id import (
    BrightIDAuraVerification,
    BrightIDMeetVerification,
)
from core.constraints.EAS import Attest, BeAttestedBy
from core.constraints.ens import HasENSVerification
from core.constraints.farcaster import (
    BeFollowedByFarcasterUser,
    DidLikedFarcasterCast,
    DidRecastFarcasterCast,
    HasFarcasterProfile,
    HasMinimumFarcasterFollower,
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
from core.constraints.twitter import (
    HasMinimumTweetCount,
    HasMinimumTwitterFollowerCount,
    HasTwitter,
)


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
