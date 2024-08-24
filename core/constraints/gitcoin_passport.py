from enum import Enum

from django.db.models.functions import Lower

from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)

from ..thirdpartyapp.gitcoin_graph import GitcoinGraph


class HasGitcoinPassportProfile(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.GITCOIN_PASSPORT.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import GitcoinPassportConnection

        user_profile = self.user_profile
        try:
            gitcoint_passport = GitcoinPassportConnection.objects.get(
                user_profile=user_profile
            )
        except GitcoinPassportConnection.DoesNotExist:
            return False
        if gitcoint_passport:
            return True
        return False


class HasMinimumHumanityScore(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.GITCOIN_PASSPORT.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import GitcoinPassportConnection

        user_profile = self.user_profile
        try:
            gitcoint_passport = GitcoinPassportConnection.objects.get(
                user_profile=user_profile
            )
        except GitcoinPassportConnection.DoesNotExist:
            return False
        if float(gitcoint_passport.score) >= float(
            self.param_values[ConstraintParam.MINIMUM.name]
        ):
            return True
        return False


class HasDonatedParam(Enum):
    MINIMUM = ConstraintParam.MINIMUM.name
    COUNT = ConstraintParam.COUNT.name
    ROUND = "round"


class HasDonatedOnGitcoin(ConstraintVerification):
    _param_keys = [
        HasDonatedParam.MINIMUM,
        HasDonatedParam.COUNT,
        HasDonatedParam.ROUND,
    ]
    app_name = ConstraintApp.GITCOIN_PASSPORT.value
    _graph_url = "https://grants-stack-indexer-v2.gitcoin.co"

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        try:
            return self.has_donated(
                self.param_values[HasDonatedParam.MINIMUM.name],
                self.param_values[HasDonatedParam.COUNT.name],
                self.param_values[HasDonatedParam.ROUND.name],
            )
        except Exception as e:
            print(e)
            return False

    def has_donated(self, min, num_of_projects, round):
        graph = GitcoinGraph()

        user_wallets = self.user_profile.wallets.values_list(
            Lower("address"), flat=True
        )

        query = """
            query getDonationsByDonorAddress($address: [String!]!, $round: String!) {
                donations(
                    first: 1000
                    filter: {
                        donorAddress: { in: $address }
                        roundId: { equalTo: $round }
                    }
                ) {
                    id
                    projectId
                    amountInUsd
                }
            }
                """
        vars = {"address": list(user_wallets), "round": str(round)}

        res = graph.send_post_request(
            {
                "query": query,
                "variables": vars,
                "operationName": "getDonationsByDonorAddress",
            }
        )
        match res:
            case {"data": {"donations": donations}} if len(donations) > 0:
                donated_projects = []
                total_donation_amount = 0
                projects_count = 0
                for donation in donations:
                    total_donation_amount += donation["amountInUsd"]
                    if donation["projectId"] not in donated_projects:
                        donated_projects.append(donation["projectId"])
                        projects_count += 1
                if (
                    total_donation_amount > float(min)
                    and projects_count >= num_of_projects
                ):
                    return True
            case _:
                return False
        return False
