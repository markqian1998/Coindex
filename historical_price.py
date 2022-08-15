from datetime import date
from prettytable import PrettyTable
from pycoingecko import CoinGeckoAPI
import coindex_utility
import json

with open("all_coins.json",'r') as load_f:
    coingecko_ids = json.load(load_f)

# To get the date we want to calculate the price
date = input("\nPlease Enter the Date You Want to Retrieve.\n(Format Example: 2018-05-15)\n")
yymmdd = date.split("-")
date_inverse = yymmdd[2] + "-" + yymmdd[1] + "-" + yymmdd[0]

print("The date to calculate is " + date)

# To get the date we need to balance the weight
date_to_weight = coindex_utility.input_date_to_retrieve(date)
yymmdd = date_to_weight.split("-")
date_to_weight_inverse = yymmdd[2] + "-" + yymmdd[1] + "-" + yymmdd[0]

print("The rebalancing date is " + date_to_weight)

# Get the rank of rebalancing date
print('Extracting data from the internet, please wait...')
top_list = coindex_utility.rank_list(date_to_weight)
print('Data Received\n')

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

# Get data of each coin of the rebalancing date
price_list = []
market_cap_list = []
cg = CoinGeckoAPI()

for coin_id in id_list:
    print('Inquire data of ' + coin_id + ' from the server...')
    data = cg.get_coin_history_by_id(id=coin_id, date=date_to_weight_inverse, localization='false')
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

# Calculate the index price for that date:
index_price = 0
then_price_list = []

for coin_id in id_list:
    print('Inquire data of ' + coin_id + ' from the server...')
    data = cg.get_coin_history_by_id(id=coin_id, date=date_inverse, localization='false')
    print('Data Received\n')
    then_price_list.append(data['market_data']['current_price']['usd'])

for i in range(20):
    index_price += weight_list[i] * then_price_list[i] 

# Print out the result nicely
msg = "Script Finished,\n" \
      "Coindex Current Price:"\
        +str(index_price)
    
coindex_utility.print_msg_box(msg=msg, indent=2, title="Summary:")

print('\nThe last rebalancing date was ' + date_to_weight + '\n')

print(table)