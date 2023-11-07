# flake8: noqa
from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from authentication.models import NetworkTypes, UserProfile, Wallet
from core.constraints import BrightIDAuraVerification, BrightIDMeetVerification
from faucet.models import Chain, WalletAccount

from .models import Constraint, NotHaveUnitapPass, Raffle, RaffleEntry

# from .utils import PrizetapContractClient

test_wallet_key = "f57fecd11c6034fd2665d622e866f05f9b07f35f253ebd5563e3d7e76ae66809"
test_rpc_url_private = "https://rpc.ankr.com/eth_sepolia"
fund_manager = "0x5802f1035AbB8B191bc12Ce4668E3815e8B7Efa0"
erc20_contract_address = "0x5363502325735d7b27162b2b3482c107fD4c5B3C"
erc721_contract_address = "0x334ab41d0F93d1d61178a21CD7A71387e5c75688"


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
        self.chain = Chain.objects.create(
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
        self.meet_constraint = Constraint.objects.create(
            name="core.BrightIDMeetVerification",
            title="BrightID meet",
            description="You have to be BrightID verified.",
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
