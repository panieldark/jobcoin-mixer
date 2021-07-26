import json
import requests
import boto3

API_BASE_URL = 'https://jobcoin.gemini.com/kept-velvet/api'
API_TRANSACTIONS_URL = '{}/transactions'.format(API_BASE_URL)

def lambda_handler(event, context):
    
    
    req = requests.get(API_TRANSACTIONS_URL)
    
    if req.status_code != 200:
        return { 'statusCode': req.status_code,
        'body': json.dumps('Issue with request from API endpoint')}
    
    transactions = req.json()
    
    
    # Get number of unread transactions
    s3 = boto3.client('s3')
    
    obj = s3.get_object(Bucket='jobcoin-mixer', Key='transaction_cache.txt')
    current_len = obj['Body'].read().decode('utf-8')

    # Update cached num
    s3 = boto3.resource('s3')
    body = "{}".format(len(transactions))
    try:
        s3.Bucket('jobcoin-mixer').put_object(Key='transaction_cache.txt', Body=body, ContentType="text/plain")
    except Exception as e:
        print(e)


    # Do an O(n) search (backwards) of the list of transactions
    # In practice, it'll be much less (O(1) practically), as we can store the size, and only check the difference between the two times checked
    new_transactions_count = len(transactions) - current_len
    

    # Grab only the new transactions, as indicated by cached count
    new_transactions = transactions[-1-new_transactions_count:-1]
    req = requests.post('http://3.83.155.124/open_requests_api/', data='new_count': new_transactions_count, 'new_transactions': new_transactions)
    req = requests.post('http://127.0.0.1:8000/open_requests_api/', data='new_count': new_transactions_count, 'new_transactions': new_transactions)
    # TODO: process the JSON body

    # for i in range(new_transactions_count):

    # TODO: query the DB, get all transactions with requests still at 'created' phase
    
    
    # TODO: Check the two against each other 
    
    # If any are a match, update the MixerRequest object's status + add the matched transaction to the Mixer Pipeline
    
    # Update the count of the cached transaction size (probably stored as a K/V in a DB)
    
    return {
        'statusCode': 200,
        'body': json.dumps('All transactions accounted for')
    }
