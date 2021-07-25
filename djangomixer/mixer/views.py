from django.shortcuts import render, redirect
import uuid
from .models import MixerRequest
from django.http import JsonResponse

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

