import csv
from prizetap.models import LineaRaffleEntries, Raffle

# Initialize empty dictionary and lists
data_dict = {}
addresses = []
chances = []

# Read the CSV file and fill the dictionary and lists
with open("lin.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file)

    for row in csv_reader:
        num = int(row[0])
        address = row[1]
        chance = int(row[2])

        data_dict[num] = {"address": address, "chance": chance}
        addresses.append(address)
        chances.append(chance)


# Split lists into chunks of size 100
def split_list(input_list, chunk_size):
    return [
        input_list[i : i + chunk_size] for i in range(0, len(input_list), chunk_size)
    ]


addresses_chunks = split_list(addresses, 100)
chances_chunks = split_list(chances, 100)

# Output
# print(data_dict)
print(addresses_chunks)
print(chances_chunks)
# print(LineaRaffleEntries.objects.all().count())
print(len(data_dict))


def add_entries(data_dict):
    linea_raffle = Raffle.objects.get(name="Linea Gas Pass")
    for i in data_dict:
        LineaRaffleEntries.objects.create(
            wallet_address=data_dict[i]["address"],
            raffle=linea_raffle,
            raffle_entry_id=i,
        )


# add_entries(data_dict)
print(LineaRaffleEntries.objects.all().count())
