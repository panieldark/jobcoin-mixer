import config
import requests
# Write your Jobcoin API client here.

def get_address_info(address):
	req = requests.get(f'{config.API_ADDRESS_URL}/{address}')
	print(f"Info for req: {address}")
	print(req.json())
	return req.status_code

def get_transactions():
	req = requests.get(config.API_TRANSACTIONS_URL)
	print("All transactions:")
	print(req.json())
	return req.status_code

def post_transaction(fromAddress, toAddress, amount):
	req = requests.post(config.API_TRANSACTIONS_URL, data={"fromAddress": fromAddress, "toAddress": toAddress, 'amount': amount})
	print(req.json())
	return req.status_code

get_address_info('Daniel')
get_transactions()

post_transaction("Daniel's dog", "Daniel's hamster", .005)