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


# @csrf_exempt
# def open_requests_api(request):
#     if request.method != "POST":
#         return HttpResponse('NOT A POST')

#     open_requests = MixerRequest.objects.filter(status='created')
    
#     # end early if no open req's
#     if not len(open_requests):
#         return HttpResponse('OK')
    
#     body = json.loads(request.body.decode('utf8'))
#     new_count = int(body['new_count'])

#     transactions_json = requests.get(API_TRANSACTIONS_URL).json()

#     # Grab only the new transactions, as indicated by cached count
#     new_transactions = transactions_json[-new_count:]



#     req_set = set()
#     for req in open_requests:
#         req_set.add(f'{req.src_address}|{req.deposit_address}')
    
#     for transaction in new_transactions:
#         print(transaction)
#         trans_string = f"{transaction['fromAddress']}|{transaction['toAddress']}"
        
#         if trans_string in req_set:
#             # TODO: do the thing
#             # get the amount, store (in new model)

#             # ['alpha', bravo, charlie, delta, echo, foxtrot, golf, hotel, india, juliet, kilo, lima, mike]


#             # separate into function to handle multiple destination wallets
#             total_percent = 100
#             # example: $100

#             while total_percent:
#                 # random_percentage (10-33%)
#                 # edge case: make sure total_percent >= random_percentage
#                 # choose a path of 3-7 wallets for random_percentage*amount from start to finish
#                 # for (iterate through wallets):
#                 # make the API calls to send money
                

#                 total_percent -= random_percent
            

            





#             # TODO: update the request

#             req_set.remove(trans_string)
#             if not req_set:
#                 break

#     # compare open requests to new transactions

    

#     return HttpResponse('OK')
