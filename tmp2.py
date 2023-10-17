import csv
from prizetap.models import LineaRaffleEntries, Raffle
from prizetap.utils import LineaPrizetapContractClient


def get_winners(raffle):
    raffle_client = LineaPrizetapContractClient(raffle)
    winner_addresses = raffle_client.get_raffle_winners()
    return winner_addresses


def set_winners(raffle, winner_addresses):
    for entry in raffle.linea_entries:
        if entry.wallet_address in winner_addresses:
            entry.is_winner = True
            entry.save()


def count_winners(raffle):
    winners = 0
    for entry in raffle.linea_entries:
        if entry.is_winner:
            winners += 1
    print(winners)


linea_raffle = Raffle.objects.get(name="Linea Gas Pass")
count_winners(linea_raffle)
winners = get_winners(linea_raffle)
print("a", winners)
print("b", len(winners))
set_winners(linea_raffle, winners)
count_winners("a", linea_raffle)
