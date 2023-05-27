import time
from contextlib import contextmanager
from django.core.cache import cache
from authentication.models import Wallet
from faucet.models import Chain, ClaimReceipt


@contextmanager
def memcache_lock(lock_id, oid, lock_expire=60):
    timeout_at = time.monotonic() + lock_expire
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, lock_expire)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


def get_tokens_of_wallet_in_chain(wallet_address: str, chain: Chain):
    try:
        wallet = Wallet.objects.get(address=wallet_address)
        claim = ClaimReceipt.objects.get(chain__chain_id=chain.chain_id, user_profile=wallet.user_profile)
        return claim.amount

    except Wallet.DoesNotExist:
        return None
    except ClaimReceipt.DoesNotExist:
        return None
