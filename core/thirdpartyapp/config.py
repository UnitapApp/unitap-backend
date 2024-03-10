import os

GITCOIN_PASSPORT_API_KEY = os.getenv("GITCOIN_PASSPORT_API_KEY", "")
GITCOIN_PASSPORT_BASE_URL = os.getenv(
    "GITCOIN_PASSPORT_BASE_URL", "https://api.scorer.gitcoin.co"
)
GITCOIN_PASSPORT_SCORER_ID = os.getenv("GITCOIN_PASSPORT_SCORER_ID", "")
LENS_BASE_URL = os.getenv("LENS_BASE_URL", "https://api-v2.lens.dev")
FARCASTER_BASE_URL = os.getenv(
    "FARCASTER_BASE_URL", "https://api.neynar.com/v2/farcaster"
)
FARCASTER_API_KEY = os.getenv("FARCASTER_API_KEY", "NEYNAR_API_DOCS")
