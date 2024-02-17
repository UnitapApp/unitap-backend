import logging

from celery import shared_task

from core.helpers import memcache_lock

from .models import TokenDistribution
from .utils import TokentapContractClient


@shared_task(bind=True)
def set_distribution_id(self):
    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return
        token_distributions_queryset = (
            TokenDistribution.objects.filter(status=TokenDistribution.Status.PENDING)
            .filter(distribution_id__isnull=True)
            .filter(tx_hash__isnull=False)
            .order_by("id")
        )
        if token_distributions_queryset.count() > 0:
            for token_distribution in token_distributions_queryset:
                try:
                    print(
                        "Setting the token_distribution "
                        f"{token_distribution.name} distribution_id"
                    )
                    contract_client = TokentapContractClient(token_distribution)

                    receipt = contract_client.web3_utils.get_transaction_receipt(
                        token_distribution.tx_hash
                    )
                    log = contract_client.get_token_distributed_log(receipt)

                    token_distribution.distribution_id = log["args"]["distributionId"]
                    onchain_distribution = contract_client.get_distribution()
                    is_valid = True
                    if (
                        token_distribution.distributor_address
                        != onchain_distribution["provider"]
                    ):
                        is_valid = False
                        logging.error(
                            "Mismatch token_distribution "
                            f"{token_distribution.pk} distributor"
                        )
                    if (
                        token_distribution.token_address
                        != onchain_distribution["token"]
                    ):
                        is_valid = False
                        logging.error(
                            f"Mismatch token_distribution {token_distribution.pk} token"
                        )
                    if (
                        token_distribution.max_number_of_claims
                        != onchain_distribution["maxNumClaims"]
                    ):
                        is_valid = False
                        logging.error(
                            "Mismatch token_distribution "
                            f"{token_distribution.pk} maxNumClaims"
                        )
                    if token_distribution.amount != str(
                        onchain_distribution["claimAmount"]
                    ):
                        is_valid = False
                        logging.error(
                            "Mismatch token_distribution "
                            f"{token_distribution.pk} claimAmount"
                        )
                    if onchain_distribution["claimsCount"] != 0:
                        is_valid = False
                        logging.error(
                            "Invalid token_distribution "
                            f"{token_distribution.pk} claimsCount"
                        )
                    if (
                        int(token_distribution.start_at.timestamp())
                        != onchain_distribution["startTime"]
                    ):
                        is_valid = False
                        logging.error(
                            "Mismatch token_distribution "
                            f"{token_distribution.pk} startTime"
                        )
                    if (
                        int(token_distribution.deadline.timestamp())
                        != onchain_distribution["endTime"]
                    ):
                        is_valid = False
                        logging.error(
                            "Mismatch token_distribution "
                            f"{token_distribution.pk} endTime"
                        )
                    if onchain_distribution["isRefunded"] == "false":
                        is_valid = False
                        logging.error(
                            "Invalid token_distribution "
                            f"{token_distribution.pk} isRefunded"
                        )
                    if not is_valid:
                        token_distribution.distribution_id = None
                        token_distribution.status = TokenDistribution.Status.REJECTED
                    token_distribution.save()
                except Exception as e:
                    logging.error(e)
