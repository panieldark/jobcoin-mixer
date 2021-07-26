from django.shortcuts import render, redirect
import uuid
from .models import MixerRequest
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import random
import math

# Create your views here.
def index(request):
    context = {}
    return render(request, "mixer/index.html", context)


def mixer_form_page(request):
    context = {}
    return render(request, "mixer/mixer_form_page.html", context)


def create_request(request):
    if not request.method == "POST":
        return redirect('mixer:mixer_form_page')
    context = {}

    src = request.POST.get('src')
    dest1 = request.POST.get('dest1')
    dest2 = request.POST.get('dest2')
    dest3 = request.POST.get('dest3')
    dest4 = request.POST.get('dest4')
    dest5 = request.POST.get('dest5')
    print(src, dest1)
    
    deposit_address = uuid.uuid4().hex
    new_req = MixerRequest.objects.create(src_address=src, dest_address = dest1, dest_address_2=dest2, dest_address_3=dest3, dest_address_4 = dest4, dest_address_5 = dest5, deposit_address = deposit_address, status = 'created')
    print(new_req)
    context['deposit_address'] = deposit_address
    return render(request, "mixer/request_created.html", context)

def create_request_ajax(request):
    if not request.is_ajax():
        return redirect('mixer:mixer_form_page')
    if not request.method == "POST":
        return JsonResponse({})
    context = {}

    src = request.POST.get('src')
    dest1 = request.POST.get('dest1')
    dest2 = request.POST.get('dest2')
    dest3 = request.POST.get('dest3')
    dest4 = request.POST.get('dest4')
    dest5 = request.POST.get('dest5')
    print(src, dest1)
    
    deposit_address = uuid.uuid4().hex
    new_req = MixerRequest.objects.create(src_address=src, dest_address = dest1, dest_address_2=dest2, dest_address_3=dest3, dest_address_4 = dest4, dest_address_5 = dest5, deposit_address = deposit_address, status = 'created')
    print(new_req)
    context['deposit_address'] = deposit_address

    if new_req:
        context['success'] = 'success'
    else:
        context['fail'] = 'fail'
    return JsonResponse(context)

API_BASE_URL = 'https://jobcoin.gemini.com/kept-velvet/api'
API_TRANSACTIONS_URL = '{}/transactions'.format(API_BASE_URL)



@csrf_exempt
def open_requests_api(request):
    if request.method != "POST":
        return HttpResponse('NOT A POST')


    try:
        open_requests = MixerRequest.objects.filter(status='created')
        
        # end early if no open req's
        if not len(open_requests):
            return HttpResponse('OK')
        
        body = json.loads(request.body.decode('utf8'))
        new_count = int(body['new_count'])

        transactions_json = requests.get(API_TRANSACTIONS_URL).json()

        # Grab only the new transactions, as indicated by cached count
        new_transactions = transactions_json[-new_count:]
        print(new_transactions)

        # Make a dict for O(1) lookups
        req_map = dict()
        for req in open_requests:
            req_map[f'{req.src_address}|{req.deposit_address}'] = req
        


        print("Requests dict:", req_map)
        for transaction in new_transactions:
            print("Transaction:", transaction)
            
            # Edge case: handle new money (no fromAddress)
            if 'fromAddress' not in transaction:
                continue
            
            trans_string = f"{transaction['fromAddress']}|{transaction['toAddress']}"
            
            if trans_string in req_map.keys():
                print('in keys', trans_string)
                amount = float(transaction['amount'])

                
                deposit_address = req_map[trans_string].deposit_address

                # compile list of destination wallets
                destinations_list = [address for address in [req_map[trans_string].dest_address, req_map[trans_string].dest_address_2, \
                    req_map[trans_string].dest_address_3, req_map[trans_string].dest_address_4, req_map[trans_string].dest_address_5] if address]

                # Take a 3% fee, add it to cryptomixer wallet, return new amount
                new_amount = take_fee(deposit_address, amount)

                # Deliver to each destination address a fraction of the new amount
                for dest in destinations_list:
                    mixed_request = mix_coins_amongst_wallets(deposit_address, dest, new_amount/len(destinations_list))
                    if not mixed_request:
                        return HttpResponse('Failed to deliver')

                
                
                # Update the request object
                request = req_map[trans_string]
                request.status = 'completed' if mixed_request else 'failed'
                request.save()


                req_map.pop(trans_string)

                # Finish early if there are no more requests to process
                if not req_map:
                    break
    
    except Exception as e:
        print("Exception:", e)
        return HttpResponse('Failed')

    return HttpResponse('OK')



def mix_coins_amongst_wallets(depositedAddress, final_address, totalAmount):
    house_wallets = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel', 'india', 'juliet']

    total_percent = 100

    while total_percent > 0:

        # edge case: make sure total_percent >= random_percentage
        random_percent = min(random.randint(9, 23), total_percent)


        # Floor to 2 decimal places
        current_amount = math.floor(random_percent*totalAmount)/100

        print("\nRandom percent:", random_percent, '%')
        print("Amount this round: ${}".format(current_amount))
        random_num_wallets = random.randint(2,5)
        
        previous_wallet = depositedAddress


        # choose a path of 2-5 wallets for random_percent*amount from start to finish
        for i in range(random_num_wallets):
            next_wallet = house_wallets[random.randint(3,7)]
            
            if previous_wallet == next_wallet:
                continue
            # make API calls to send money
            try:
                print(f"{previous_wallet} -> {next_wallet}: ${current_amount}")
                req = requests.post(API_TRANSACTIONS_URL, data={"fromAddress": previous_wallet, "toAddress": next_wallet, 'amount': current_amount})
                if int(req.status_code) >= 400:
                    raise Exception(req.status_code, req.reason)
            except Exception as e:
                print(e)
                return False
            
            previous_wallet = next_wallet
        
        print(f"FINAL: {previous_wallet} -> {final_address}: ${current_amount}")
        # finally, send this chunk of money to final destination
        req = requests.post(API_TRANSACTIONS_URL, data={"fromAddress": previous_wallet, "toAddress": final_address, 'amount': current_amount})


        total_percent -= random_percent
    
    return True

def take_fee(deposit_address, origAmount):
    # 3% fee, floored to 2 dec places
    fee = math.floor(3 * origAmount)/100
    print(f"FEE: {deposit_address} -> {'CryptoMixer'}: ${fee}")
    req = requests.post(API_TRANSACTIONS_URL, data={"fromAddress": deposit_address, "toAddress": 'CryptoMixer', 'amount': fee})
    new_amount = origAmount - fee
    return new_amount