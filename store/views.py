from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder, processPayment

def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

##### PROCESS ORDER NEED TO BE WORKED-FINISH ############
def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	from random import choice

	transaction_ref = choice(['wx', 'uz', '79']) + str(order.id) + choice(['ms', 'yv', 'tk'])
	thirdy_party_ref = choice(['lz', '97', 'mw']) + str(order.id) + choice(['ns', 'ru', 'na'])
	print(transaction_ref)

	phone = data['paymentMethod']
	print("######################## PHONE NUMBER BEGIN")
	print(phone)
	print("###################### END ####################")
	print(order)
	print(customer)
	
	print("###########################################")

	if total == order.get_cart_total:

		processPayment(amount=total, clientePhone=phone, transaction_reference=transaction_ref, thirdy_party_reference=thirdy_party_ref)

		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	

	return JsonResponse('Payment submitted..', safe=False)


#### NEED REVIEW #############

def login_customer(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                customer = user.customer  # Verifica se é Customer
                login(request, user)
                return redirect('store')  # exemplo
            except Customer.DoesNotExist:
                messages.error(request, 'Você não é um cliente.')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'store/login_customer.html')


def login_store(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                loja = user.store  # Verifica se é Store
                login(request, user)
                return redirect('cadastrar_produto')
            except Store.DoesNotExist:
                messages.error(request, 'Você não é uma loja.')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'store/login_store.html')

def logout_view(request):
    logout(request)
    return redirect('store')

#### CADASTRAR PRODUTO ############

@login_required
def cadastrar_produto(request):
    try:
        loja = request.user.store
    except Store.DoesNotExist:
        return redirect('login_store')

    if request.method == 'POST':
        nome = request.POST['nome']
        preco = request.POST['preco']
        stock = request.POST['stock']
        digital = request.POST.get('digital') == 'on'
        imagem = request.FILES.get('imagem')

        produto = Product.objects.create(
            name=nome,
            price=preco,
            stock=stock,
            digital=digital,
            image=imagem,
            store=loja
        )

        # salvar especificações (repetidamente, tipo chave=valor)
        chaves = request.POST.getlist('chave')
        valores = request.POST.getlist('valor')
        for chave, valor in zip(chaves, valores):
            Spec.objects.create(produto=produto, chave=chave, valor=valor)

        return redirect('ver_produto', produto_id=produto.id)

    return render(request, 'store/cadastrar_produto.html')

def ver_produto(request, produto_id):
    produto = get_object_or_404(Product, id=produto_id)
    return render(request, 'store/ver_produto.html', {'produto': produto})

from django.contrib.auth.models import User
from .models import Customer, Store

def register_customer(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        nome = request.POST['name']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            Customer.objects.create(user=user, name=nome, email=email)
            login(request, user)
            return redirect('store')

    return render(request, 'store/register_customer.html')


def register_store(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        phone = request.POST['phone']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            Store.objects.create(user=user, name=name, email=email, phone=phone)
            login(request, user)
            return redirect('cadastrar_produto')

    return render(request, 'store/register_store.html')
