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
EAS_BASE_URL = {
    "ethereum": os.getenv("ETHEREUM_EAS_BASE_URL", "https://easscan.org/graphql"),
    "arbitrum": os.getenv(
        "ARBITRUM_EAS_BASE_URL", "https://arbitrum.easscan.org/graphql"
    ),
    "base": os.getenv("BASE_EAS_BASE_URL", "https://base.easscan.org/graphql"),
    "linea": os.getenv("LINEA_EAS_BASE_URL", "https://linea.easscan.org/graphql"),
    "optimism": os.getenv(
        "OPTIMISM_EAS_BASE_URL", "https://optimism.easscan.org/graphql"
    ),
}
NFT_PASS_SUBGRAPH_URL = os.getenv("NFT_PASS_SUBGRAPH_URL", "https://api.studio.thegraph.com/query/73675/unitap-pass-eth/version/latest")