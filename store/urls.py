from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    
	#Logins and Logout
    path('login/customer/', views.login_customer, name='login_customer'),
    path('login/store/', views.login_store, name='login_store'),
    path('logout/', views.logout_view, name='logout'),
    
	path('register/customer/', views.register_customer, name='register_customer'),
    path('register/store/', views.register_store, name='register_store'),

    #Product visualization and registration
	path('produto/cadastrar/', views.cadastrar_produto, name='cadastrar_produto'),
    path('produto/<int:produto_id>/', views.ver_produto, name='ver_produto'),

]