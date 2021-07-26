from django.shortcuts import render, redirect
import uuid
from .models import MixerRequest
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

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
    print(src, dest1)
    
    deposit_address = uuid.uuid4().hex
    new_req = MixerRequest.objects.create(src_address=src, dest_address = dest1, deposit_address = deposit_address, status = 'created')
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
    print(src, dest1)
    
    deposit_address = uuid.uuid4().hex
    new_req = MixerRequest.objects.create(src_address=src, dest_address = dest1, deposit_address = deposit_address, status = 'created')
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


        # Make a dict for O(1) lookups
        req_map = dict()
        for req in open_requests:
            req_map[f'{req.src_address}|{req.deposit_address}'] = req
        


        for transaction in new_transactions:
            print(transaction)
            trans_string = f"{transaction['fromAddress']}|{transaction['toAddress']}"
            
            if trans_string in req_map.keys():

                amount = float(transaction['amount'])

                
                
                mixed_request = mix_coins_amongst_wallets(transaction['fromAddress'], transaction['toAddress'], amount)
                
                
                # Update the request object
                request = req_map[trans_string]
                request.status = 'completed' if mixed_request else 'failed'
                request.save()


                req_map.pop(trans_string)

                # Finish early if there are no more requests to process
                if not req_map:
                    break
    
    except Exception as e:
        print(e)
        return HttpResponse('Failed')

    return HttpResponse('OK')



def mix_coins_amongst_wallets(fromAddress, toAddress, amount):
    house_wallets = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel', 'india', 'juliet']

    total_percent = 100

    while total_percent:

        # edge case: make sure total_percent >= random_percentage
        random_percent = min(random.randint(10, 33), total_percent)/100

        random_num_wallets = random.randint(3,7)
        
        previous_wallet = fromAddress


        # choose a path of 3-7 wallets for random_percent*amount from start to finish
        for i in range(random_num_wallets):
            next_wallet = house_wallets[random.randint(0,9)]
            
            if previous_wallet == next_wallet:
                continue
            # make API calls to send money
            try:
                req = requests.post(API_TRANSACTIONS_URL, data={"fromAddress": previous_wallet, "toAddress": next_wallet, 'amount': amount*random_percent})
                if int(req.status_code) >= 400:
                    raise Exception(req.status_code)
            except Exception as e:
                print(e)
                return False
            
            previous_wallet = next_wallet
        
        # finally, send this chunk of money to final destination
        req = requests.post(API_TRANSACTIONS_URL, data={"fromAddress": previous_wallet, "toAddress": toAddress, 'amount': amount*random_percent})


        total_percent -= random_percent
    
    return True
