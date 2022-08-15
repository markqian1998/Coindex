from prettytable import PrettyTable
from pycoingecko import CoinGeckoAPI
import coindex_utility
import json

with open("all_coins.json",'r') as load_f:
    coingecko_ids = json.load(load_f)

# Index is quarterly rebalanced
# This function returns the latest rebalance date we referred to
date_string = coindex_utility.date_to_retrieve()
date_string_inverse = coindex_utility.date_to_retrieve_inverse()

# This function returns the corresponding rank of the date input
# Ranking data source: Coincodex
print('Extracting data from the internet, please wait...')
top_list = coindex_utility.rank_list(date_string)
print('Data Received')

# Get the list of Stablecoins that we need to remove from the rank
cg = CoinGeckoAPI()
stablecoins = []
stablecoins_data = cg.get_coins_markets(vs_currency='usd', category='stablecoins', sparkline='false')
# List of stablecoin symbols (latest)
for sc in stablecoins_data:
    stablecoins.append(sc['symbol'])

# Filter out the stablecoins
for i in range(len(top_list)):
    top_list[i] = top_list[i].lower()

no_stablecoin = []
for symbol in top_list:
    if symbol in stablecoins:
        continue
    else:
        no_stablecoin.append(symbol)

# Slice the top 20 we need
top_list = no_stablecoin[:20]

# Get GoinGecko ids from the symbols we have
id_list = []
for symbol in top_list:
    # Since there are several coins share the same symbol....
    # Below is a way to fix it
    id_count = 0
    temp_list = []
    for item in coingecko_ids:
        if symbol == item['symbol']:
            id_count += 1
            temp_list.append(item['id'])

    if id_count>1:
        temp_len_list = []
        
        for temp in temp_list:
            temp_len_list.append(len(temp))
            
        index = temp_len_list.index(min(temp_len_list))
        id_list.append(temp_list[index])
    else:
        id_list.append(temp_list[0])

# Get data of each coin of the corresponding date
price_list = []
market_cap_list = []
cg = CoinGeckoAPI()

for coin_id in id_list:
    print('Inquire data of ' + coin_id + ' from the server...')
    data = cg.get_coin_history_by_id(id=coin_id, date=date_string_inverse, localization='false')
    print('Data Received\n')
    price_list.append(data['market_data']['current_price']['usd'])
    market_cap_list.append(data['market_data']['market_cap']['usd'])

# Calculate the Index weighting balance of that referred date
total_market_cap = sum(market_cap_list)

table = PrettyTable(['Rank', 'Symbol','Weight'])
weight_list = []
mc_accumulation = 0
weight_accumulation = 0

for i in range(20):
    portion = 1 - weight_accumulation
    denominator = sum(market_cap_list[i:])
    inner_portion = market_cap_list[i]/denominator
    weight = min(0.15, inner_portion*portion)
    weight_list.append(weight)
    weight_accumulation += weight
    table.add_row([i+1, top_list[i], '{:.2%}'.format(weight)])

# Calculate the index price for now:
index_price = 0
now_prices = cg.get_price(ids=id_list, vs_currencies='usd')

for i in range(20):
    id = id_list[i]
    index_price += weight_list[i] * now_prices[id]['usd']

# Print out the result nicely
msg = "Script Finished,\n" \
      "Coindex Current Price:"\
        +str(index_price)
    
coindex_utility.print_msg_box(msg=msg, indent=2, title="Summary:")

print('\nThe last rebalancing date was ' + date_string + '\n')

print(table)
