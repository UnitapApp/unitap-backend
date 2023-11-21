import base64
import json
from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from authentication.models import NetworkTypes, UserProfile, Wallet
from faucet.models import Chain, WalletAccount

from .models import Constraint, NotHaveUnitapPass, Raffle, RaffleEntry

# from .utils import PrizetapContractClient

test_wallet_key = "f57fecd11c6034fd2665d622e866f05f9b07f35f253ebd5563e3d7e76ae66809"
test_rpc_url_private = "https://rpc.ankr.com/eth_sepolia"
fund_manager = "0x5802f1035AbB8B191bc12Ce4668E3815e8B7Efa0"
erc20_contract_address = "0x57b2BA844fD37F20E9358ABaa6995caA4fCC9994"
erc721_contract_address = "0xDB7bA3A3cbEa269b993250776aB5B275a5F004a0"


# # Create your tests here.


class BaseTestCase(APITestCase):
    def setUp(self):
        self.user_profile = UserProfile.objects.create(
            user=User.objects.create_user(username="test", password="1234"),
            initial_context_id="test",
            username="test",
        )
        Wallet.objects.create(
            user_profile=self.user_profile,
            wallet_type=NetworkTypes.EVM,
            address="0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb",
        )
        self.wallet = WalletAccount.objects.create(
            name="Sepolia Chain Wallet",
            private_key=test_wallet_key,
            network_type=NetworkTypes.EVM,
        )
        self.chain = self.create_mumbai_chain()
        self.meet_constraint = Constraint.objects.create(
            name="core.BrightIDMeetVerification",
            title="BrightID meet",
            description="You have to be BrightID verified.",
        )

    def create_polygon_chain(self):
        return Chain.objects.create(
            chain_name="Polygon",
            wallet=self.wallet,
            rpc_url_private="https://rpc.ankr.com/polygon",
            explorer_url="https://polygonscan.com/",
            fund_manager_address=fund_manager,
            native_currency_name="MATIC",
            symbol="MATIC",
            chain_id="137",
            max_claim_amount=1e11,
        )

    def create_mumbai_chain(self):
        return Chain.objects.create(
            chain_name="Mumbai",
            wallet=self.wallet,
            rpc_url_private="https://rpc.ankr.com/polygon_mumbai",
            explorer_url="https://mumbai.polygonscan.com/",
            fund_manager_address=fund_manager,
            native_currency_name="MATIC",
            symbol="MATIC",
            chain_id="80001",
            max_claim_amount=1e11,
        )


class RaffleTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.raffle = Raffle.objects.create(
            name="Test Raffle",
            description="Test Raffle Description",
            contract=erc20_contract_address,
            raffleId=1,
            creator_profile=self.user_profile,
            prize_amount=1e14,
            prize_asset="0x0000000000000000000000000000000000000000",
            prize_name="Test raffle",
            prize_symbol="Eth",
            decimals=18,
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=1),
            max_number_of_entries=2,
            status=Raffle.Status.VERIFIED,
        )
        self.raffle.constraints.set([self.meet_constraint])

    def test_raffle_creation(self):
        self.assertEqual(Raffle.objects.count(), 1)
        self.assertEqual(Raffle.objects.first(), self.raffle)
        self.assertEqual(Raffle.objects.first().constraints.count(), 1)
        self.assertEqual(Raffle.objects.first().constraints.first(), self.meet_constraint)

    def test_raffle_claimable(self):
        self.assertTrue(self.raffle.is_claimable)

    def test_raffle_expiration(self):
        self.assertFalse(self.raffle.is_expired)

        self.raffle.deadline = timezone.now()
        self.raffle.save()

        self.assertTrue(self.raffle.is_expired)
        self.assertFalse(self.raffle.is_claimable)

    def test_raffle_is_active(self):
        self.assertTrue(self.raffle.is_active)
        self.raffle.is_active = False
        self.assertFalse(self.raffle.is_active)
        self.assertFalse(self.raffle.is_claimable)

    @patch("prizetap.models.Raffle.is_maxed_out")
    def test_raffle_claimable_if_maxed_out(self, mock_method):
        mock_method.return_value = True
        self.assertTrue(self.raffle.is_maxed_out)
        self.assertFalse(self.raffle.is_claimable)

    def test_raffle_maxed_out(self):
        self.raffle.entries.set(
            [RaffleEntry.objects.create(raffle=self.raffle, user_profile=self.user_profile, multiplier=2)]
        )
        self.assertFalse(self.raffle.is_maxed_out)
        entry: RaffleEntry = self.raffle.entries.first()
        entry.tx_hash = "0x0"
        entry.save()

        self.assertFalse(self.raffle.is_maxed_out)
        self.assertTrue(self.raffle.is_claimable)

        RaffleEntry.objects.create(
            raffle=self.raffle,
            user_profile=UserProfile.objects.create(
                user=User.objects.create_user(username="test_2", password="1234"),
                initial_context_id="test_2",
                username="test_2",
            ),
            multiplier=1,
        )

        self.assertTrue(self.raffle.is_maxed_out)
        self.assertFalse(self.raffle.is_claimable)


class RaffleAPITestCase(RaffleTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.raffle_data = {
            "name": "test_create_raffle_api",
            "description": "A test raffle",
            "contract": erc20_contract_address,
            "creator_name": "unitap",
            "creator_address": self.wallet.address,
            "twitter_url": "https://twitter.com/unitap_app",
            "email_url": "blobl@gmail.com",
            "prize_amount": "100000000",
            "prize_asset": "0x0000000000000000000000000000000000000000",
            "prize_name": "1 ETH",
            "prize_symbol": "ETH",
            "decimals": 18,
            "chain": self.chain.pk,
            "constraints": [self.meet_constraint.pk],
            "constraint_params": base64.b64encode(json.dumps({}).encode("utf-8")).decode("utf-8"),
            "deadline": "2023-09-25 21:00",
            "max_number_of_entries": 1000,
            "start_at": "2023-09-25 10:00",
            "winners_count": 5,
        }

    @patch("authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status", lambda a, b, c: (True, None))
    def test_raffle_list(self):
        self.raffle.constraints.add(
            Constraint.objects.create(
                name="core.BrightIDAuraVerification",
                title="BrightID aura",
                description="You have to be Aura verified.",
            )
        )
        response = self.client.get(reverse("raffle-list"))
        raffle = response.data[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(raffle["constraints"]), 2)
        self.assertEqual(raffle["constraints"][1]["name"], "core.BrightIDAuraVerification")
        self.assertEqual(raffle["number_of_entries"], 0)
        self.assertEqual(raffle["user_entry"], None)
        self.assertEqual(raffle["winner_entry"], None)

    def test_raffle_enrollment_authentication(self):
        response = self.client.post(reverse("raflle-enrollment", kwargs={"pk": self.raffle.pk}))
        self.assertEqual(response.status_code, 401)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (False, None),
    )
    def test_raffle_enrollment_validation(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(reverse("raflle-enrollment", kwargs={"pk": self.raffle.pk}))
        self.assertEqual(response.status_code, 403)

    def test_create_raffle(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(reverse("create-raffle"), self.raffle_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Raffle.objects.count(), 2)
        self.assertEqual(Raffle.objects.get(pk=2).name, "test_create_raffle_api")

    def test_create_raffle_with_invalid_constraint_params(self):
        constraint = Constraint.objects.create(
            name="faucet.HasClaimedGasInThisRound",
            title="Has claimed gas in the round",
            description="You should have claimed gas in this round",
        )
        self.client.force_authenticate(user=self.user_profile.user)
        self.raffle_data["constraints"] = [constraint.pk]
        response = self.client.post(reverse("create-raffle"), self.raffle_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Raffle.objects.count(), 1)
        raffle = None
        try:
            raffle = Raffle.objects.get(pk=2)
        except Raffle.DoesNotExist:
            pass

        self.assertEqual(raffle, None)

    def test_create_raffle_with_invalid_winners_count(self):
        self.client.force_authenticate(user=self.user_profile.user)
        self.raffle_data["max_number_of_entries"] = 10
        self.raffle_data["winners_count"] = 11
        response = self.client.post(reverse("create-raffle"), self.raffle_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Raffle.objects.count(), 1)
        raffle = None
        try:
            raffle = Raffle.objects.get(pk=2)
        except Raffle.DoesNotExist:
            pass

        self.assertEqual(raffle, None)

    def test_create_raffle_with_invalid_chain_id(self):
        Chain.objects.create(
            chain_name="Sepolia",
            wallet=self.wallet,
            rpc_url_private=test_rpc_url_private,
            explorer_url="https://sepolia.etherscan.io/",
            fund_manager_address=fund_manager,
            native_currency_name="ETH",
            symbol="ETH",
            chain_id="11155111",
            max_claim_amount=1e11,
        )

        self.client.force_authenticate(user=self.user_profile.user)
        self.raffle_data["chain"] = 3
        response = self.client.post(reverse("create-raffle"), self.raffle_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Raffle.objects.count(), 1)
        raffle = None
        try:
            raffle = Raffle.objects.get(pk=2)
        except Raffle.DoesNotExist:
            pass

        self.assertEqual(raffle, None)

    def test_create_raffle_with_invalid_contract_address(self):
        self.client.force_authenticate(user=self.user_profile.user)
        self.raffle_data["contract"] = "0x5363502325735d7b27162b2b3482c107fD4c5B3C"
        response = self.client.post(reverse("create-raffle"), self.raffle_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Raffle.objects.count(), 1)
        raffle = None
        try:
            raffle = Raffle.objects.get(pk=2)
        except Raffle.DoesNotExist:
            pass

        self.assertEqual(raffle, None)

    def test_set_raffle_tx(self):
        self.client.force_authenticate(user=self.user_profile.user)
        tx_hash = "0xb164ab20b5b9ada53906572dee4847b46f7be7b692c805619eb35be2d5053ace"
        response = self.client.post(reverse("set-raffle-tx", kwargs={"pk": self.raffle.pk}), data={"tx_hash": tx_hash})
        self.raffle.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.raffle.tx_hash, tx_hash)

    def test_set_not_owned_raffle_tx(self):
        self.client.force_authenticate(user=self.user_profile.user)
        self.raffle.creator_profile = UserProfile.objects.create(
            user=User.objects.create_user(username="test_2", password="1234"),
            initial_context_id="test_2",
            username="test_2",
        )
        self.raffle.save()
        tx_hash = "0xb164ab20b5b9ada53906572dee4847b46f7be7b692c805619eb35be2d5053ace"
        response = self.client.post(reverse("set-raffle-tx", kwargs={"pk": self.raffle.pk}), data={"tx_hash": tx_hash})
        self.raffle.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.raffle.tx_hash, None)

    def test_overwrite_raffle_tx(self):
        self.client.force_authenticate(user=self.user_profile.user)
        tx_hash = "0xb164ab20b5b9ada53906572dee4847b46f7be7b692c805619eb35be2d5053ace"
        self.client.post(reverse("set-raffle-tx", kwargs={"pk": self.raffle.pk}), data={"tx_hash": tx_hash})
        new_tx_hash = "0xd2f06c076e688de472fcb7e8a62c08e261947e28c073725a4095e362f1fa2d6a"
        response = self.client.post(
            reverse("set-raffle-tx", kwargs={"pk": self.raffle.pk}), data={"tx_hash": new_tx_hash}
        )
        self.raffle.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.raffle.tx_hash, tx_hash)

    def test_set_invalid_raffle_tx(self):
        self.client.force_authenticate(user=self.user_profile.user)
        tx_hash = "0xb164ab20b5b9ada53906572dee4847b46f7be7b692c805619eb35be2d5053ac"
        response = self.client.post(reverse("set-raffle-tx", kwargs={"pk": self.raffle.pk}), data={"tx_hash": tx_hash})
        self.raffle.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.raffle.tx_hash, None)

    def test_get_valid_chains(self):
        self.create_polygon_chain()
        response = self.client.get(reverse("get-valid-chains"))
        self.assertEqual(response.status_code, 200)
        data = response.data["data"]
        self.assertEqual(data[0]["chain_id"], "80001")
        self.assertEqual(data[0]["erc20_prizetap_addr"], "0x57b2BA844fD37F20E9358ABaa6995caA4fCC9994")
        self.assertEqual(data[0]["erc721_prizetap_addr"], "0xDB7bA3A3cbEa269b993250776aB5B275a5F004a0")
        self.assertEqual(data[1]["chain_id"], "137")
        self.assertEqual(data[1]["erc20_prizetap_addr"], "0xB521C36F76d28Edb287346C9D649Fa1A60754f04")
        self.assertEqual(data[1]["erc721_prizetap_addr"], "0xb68D3f2946Bf477978c68b509FD9f85E9e20F869")

    def test_get_user_raffles(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.get(reverse("get-user-raffles"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["pk"], self.raffle.pk)
        self.assertEqual(response.data[0]["name"], self.raffle.name)

    def test_get_constraints(self):
        response = self.client.get(reverse("get-constraints"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["pk"], self.meet_constraint.pk)
        self.assertEqual(response.data[0]["name"], self.meet_constraint.name)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (False, None),
    )
    def test_get_raffle_constraints(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.get(reverse("get-raffle-constraints", kwargs={"raffle_pk": self.raffle.pk}))
        data = response.data["constraints"][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["pk"], self.meet_constraint.pk)
        self.assertEqual(data["is_verified"], False)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_get_raffle_constraints_when_is_verified(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.get(reverse("get-raffle-constraints", kwargs={"raffle_pk": self.raffle.pk}))
        data = response.data["constraints"][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["pk"], self.meet_constraint.pk)
        self.assertEqual(data["is_verified"], True)


class RaffleEntryTestCase(RaffleTestCase):
    def setUp(self):
        super().setUp()


class RaffleEntryAPITestCase(RaffleEntryTestCase):
    def setUp(self):
        super().setUp()

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_raffle_enrollment(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(reverse("raflle-enrollment", kwargs={"pk": self.raffle.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.raffle.entries.count(), 1)
        entry: RaffleEntry = self.raffle.entries.first()
        self.assertEqual(entry.user_profile, self.user_profile)
        self.assertEqual(entry.is_winner, False)
        self.assertEqual(self.raffle.number_of_entries, 1)

    @patch("prizetap.models.Raffle.is_claimable", new_callable=PropertyMock)
    @patch("authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status", lambda a, b, c: (True, None))
    def test_not_claimable_raffle_enrollment(self, is_claimable_mock: PropertyMock):
        is_claimable_mock.return_value = False
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(reverse("raflle-enrollment", kwargs={"pk": self.raffle.pk}))
        self.assertEqual(response.status_code, 403)

    @patch("authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status", lambda a, b, c: (True, None))
    def test_set_raffle_enrollment_tx(self):
        entry = RaffleEntry.objects.create(raffle=self.raffle, user_profile=self.user_profile)
        self.client.force_authenticate(user=self.user_profile.user)
        tx_hash = "0xc9f4401d848bf61bd8e225fa800ab259018a917b55b0aa6aa1beefb2747d4af5"
        response = self.client.post(reverse("set-enrollment-tx", kwargs={"pk": entry.pk}), data={"tx_hash": tx_hash})
        self.assertEqual(response.status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.tx_hash, tx_hash)
        self.assertEqual(response.data["entry"]["tx_hash"], tx_hash)
        self.assertEqual(self.raffle.number_of_entries, 1)

    @patch("authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status", lambda a, b, c: (True, None))
    def test_set_not_owned_raffle_enrollment_tx_failure(self):
        entry = RaffleEntry.objects.create(
            raffle=self.raffle,
            user_profile=UserProfile.objects.create(
                user=User.objects.create_user(username="test_2", password="1234"),
                initial_context_id="test_2",
                username="test_2",
            ),
        )
        self.client.force_authenticate(user=self.user_profile.user)
        tx_hash = "0xc9f4401d848bf61bd8e225fa800ab259018a917b55b0aa6aa1beefb2747d4af5"
        response = self.client.post(reverse("set-enrollment-tx", kwargs={"pk": entry.pk}), data={"tx_hash": tx_hash})
        self.assertEqual(response.status_code, 403)
        entry.refresh_from_db()
        self.assertEqual(entry.tx_hash, None)

    @patch("authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status", lambda a, b, c: (True, None))
    def test_duplicate_set_raffle_enrollment_tx_failure(self):
        tx_hash = "0xc9f4401d848bf61bd8e225fa800ab259018a917b55b0aa6aa1beefb2747d4af5"
        entry = RaffleEntry.objects.create(raffle=self.raffle, user_profile=self.user_profile, tx_hash=tx_hash)
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(reverse("set-enrollment-tx", kwargs={"pk": entry.pk}), data={"tx_hash": tx_hash})
        self.assertEqual(response.status_code, 403)

    @patch("authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status", lambda a, b, c: (True, None))
    def test_set_claiming_prize_tx(self):
        entry = RaffleEntry.objects.create(raffle=self.raffle, user_profile=self.user_profile, is_winner=True)
        self.client.force_authenticate(user=self.user_profile.user)
        tx_hash = "0xc9f4401d848bf61bd8e225fa800ab259018a917b55b0aa6aa1beefb2747d4af5"
        response = self.client.post(
            reverse("set-claiming-prize-tx", kwargs={"pk": self.raffle.pk}), data={"tx_hash": tx_hash}
        )
        self.assertEqual(response.status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.claiming_prize_tx, tx_hash)
        self.assertEqual(response.data["entry"]["claiming_prize_tx"], tx_hash)

    @patch("authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status", lambda a, b, c: (True, None))
    def test_set_not_owned_claim_prize_failure(self):
        RaffleEntry.objects.create(raffle=self.raffle, user_profile=self.user_profile)
        entry = RaffleEntry.objects.create(
            raffle=self.raffle,
            user_profile=UserProfile.objects.create(
                user=User.objects.create_user(username="test_2", password="1234"),
                initial_context_id="test_2",
                username="test_2",
            ),
            is_winner=True,
        )
        self.client.force_authenticate(user=self.user_profile.user)
        tx_hash = "0xc9f4401d848bf61bd8e225fa800ab259018a917b55b0aa6aa1beefb2747d4af5"
        response = self.client.post(
            reverse("set-claiming-prize-tx", kwargs={"pk": self.raffle.pk}), data={"tx_hash": tx_hash}
        )
        self.assertEqual(response.status_code, 403)
        entry.refresh_from_db()
        self.assertEqual(entry.claiming_prize_tx, None)

    @patch("authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status", lambda a, b, c: (True, None))
    def test_duplicate_claiming_prize_tx_failure(self):
        tx_hash = "0xc9f4401d848bf61bd8e225fa800ab259018a917b55b0aa6aa1beefb2747d4af5"
        RaffleEntry.objects.create(raffle=self.raffle, user_profile=self.user_profile, claiming_prize_tx=tx_hash)
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("set-claiming-prize-tx", kwargs={"pk": self.raffle.pk}), data={"tx_hash": tx_hash}
        )
        self.assertEqual(response.status_code, 403)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_get_raffle_entry(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(reverse("raflle-enrollment", kwargs={"pk": self.raffle.pk}))
        first_entry = self.raffle.entries.first()
        response = self.client.get(reverse("raflle-enrollment-detail", kwargs={"pk": first_entry.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.data["entry"]
        self.assertEqual(data["pk"], first_entry.pk)
        self.assertEqual(data["chain"], self.raffle.chain.chain_id)
        self.assertEqual(data["user_profile"]["pk"], self.user_profile.pk)
        self.assertEqual(data["raffle"]["name"], self.raffle.name)
        self.assertEqual(data["raffle"]["raffleId"], self.raffle.raffleId)


class UtilsTestCase(RaffleTestCase):
    def setUp(self):
        super().setUp()
        self.mainnet_chain = Chain.objects.create(
            chain_name="ETH",
            wallet=self.wallet,
            rpc_url_private="https://rpc.ankr.com/eth",
            explorer_url="https://etherscan.io/",
            fund_manager_address=fund_manager,
            native_currency_name="ETH",
            symbol="ETH",
            chain_id="1",
            max_claim_amount=1e11,
        )

    def test_unitappass_contraint(self):
        constraint = NotHaveUnitapPass(self.user_profile)
        self.assertTrue(constraint.is_observed())

    # def test_set_winner(self):
    #     self.raffle.raffleId = 2
    #     client = PrizetapContractClient(self.raffle)
    #     winner = client.get_raffle_winner()
    #     self.assertEqual(winner, "0x59351584417882EE549eE3B9BF398485ddB5B7E9")
