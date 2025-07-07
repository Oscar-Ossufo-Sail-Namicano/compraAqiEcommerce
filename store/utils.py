import json
from .models import *

def cookieCart(request):

	#Create empty cart for now for non-logged in user
	try:
		cart = json.loads(request.COOKIES['cart'])
	except:
		cart = {}
		print('CART:', cart)

	items = []
	order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
	cartItems = order['get_cart_items']

	for i in cart:
		#We use try block to prevent items in cart that may have been removed from causing error
		try:	
			if(cart[i]['quantity']>0): #items with negative quantity = lot of freebies  
				cartItems += cart[i]['quantity']

				product = Product.objects.get(id=i)
				total = (product.price * cart[i]['quantity'])

				order['get_cart_total'] += total
				order['get_cart_items'] += cart[i]['quantity']

				item = {
				'id':product.id,
				'product':{'id':product.id,'name':product.name, 'price':product.price, 
				'imageURL':product.imageURL}, 'quantity':cart[i]['quantity'],
				'digital':product.digital,'get_total':total,
				}
				items.append(item)

				if product.digital == False:
					order['shipping'] = True
		except:
			pass
			
	return {'cartItems':cartItems ,'order':order, 'items':items}

def cartData(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		cookieData = cookieCart(request)
		cartItems = cookieData['cartItems']
		order = cookieData['order']
		items = cookieData['items']

	return {'cartItems':cartItems ,'order':order, 'items':items}

	
def guestOrder(request, data):
	name = data['form']['name']
	email = data['form']['phone']

	cookieData = cookieCart(request)
	items = cookieData['items']

	customer, created = Customer.objects.get_or_create(
			email=email,
			)
	customer.name = name
	customer.save()

	order = Order.objects.create(
		customer=customer,
		complete=False,
		)

	for item in items:
		product = Product.objects.get(id=item['id'])
		orderItem = OrderItem.objects.create(
			product=product,
			order=order,
			quantity=(item['quantity'] if item['quantity']>0 else -1*item['quantity']), # negative quantity = freebies
		)
	return customer, order

#--------------------------- API PAYMENT ------------------------------#
from pprint import pprint
import os
from portalsdk import APIContext, APIMethodType, APIRequest

service_provider_code = os.getenv('SERVICE_PROVIDER_CODE')
api_key = os.getenv('API_KEY')
public_key = os.getenv('PUBLIC_KEY')
api_address = os.getenv('API_ADDRESS')
api_path = os.getenv('API_PATH')
api_port = os.getenv('API_PORT')

pprint(f"""
	{api_key},
	{api_address},
	{api_port},
	{api_path},
	{public_key},
	{service_provider_code}"""
)


def processPayment(clientePhone, amount, transaction_reference, thirdy_party_reference):
    api_context = APIContext()
    api_context.api_key = api_key
    api_context.public_key = public_key
    api_context.ssl = True
    api_context.method_type = APIMethodType.POST
    api_context.address = api_address
    api_context.port = int(api_port)
    api_context.path = api_path
    
    api_context.add_header('Origin', '*')

    api_context.add_parameter('input_TransactionReference',transaction_reference)
    api_context.add_parameter('input_CustomerMSISDN',clientePhone)
    api_context.add_parameter('input_Amount',amount)
    api_context.add_parameter('input_ThirdPartyReference',thirdy_party_reference)
    api_context.add_parameter('input_ServiceProviderCode',service_provider_code)


    api_request = APIRequest(api_context)
    result = api_request.execute()

    pprint(result.status_code)
    pprint(result.headers)
    pprint(result.body)