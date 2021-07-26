import config
import requests
import json
# Write your Jobcoin API client here.

def get_address_info(address):
	req = requests.get(f'{config.API_ADDRESS_URL}/{address}')
	return req.json()

def get_transactions():
	req = requests.get(config.API_TRANSACTIONS_URL)

	return req.json()

def post_transaction(fromAddress, toAddress, amount):
	req = requests.post(config.API_TRANSACTIONS_URL, data={"fromAddress": fromAddress, "toAddress": toAddress, 'amount': amount})
	return req.json()


