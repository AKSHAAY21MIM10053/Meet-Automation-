"""
URL configuration for MeetBotProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from MeetApp import views


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('register/', views.register, name='register'), #working
    path('registercon/', views.registercon, name='registercon'),  #working
    path('registerauthentication/', views.registerauthentication, name='registerauthentication'), 
    path('operate_item/<str:item_id>/', views.operate_item, name='operate_item'),
    path('loginone/', views.loginone, name='loginone'),
    path('logintwo/', views.logintwo, name='logintwo'),
    path('logout/', views.logoutp, name='logout'),
    path('home/', views.home, name='home'),
    path('adminacess/', views.adminacess, name='adminacess'),
    path('', views.mainhome, name='mainhome'),
    path('meetbot/', views.Meetbot, name='Meetbot'),
    path('messagedisplay/', views.MessageDisplay, name='MessageDisplay'),
    path('updatepassword/', views.updatepassword, name='updatepassword'),
    path('updatepasswordconfirm/', views.updatepasswordconfirm, name='updatepasswordconfirm'),
    path('Profile/', views.Profile, name='Profile'),
    path('editprofile/', views.Editprofile, name='Editprofile'),
    path('SendMessage/', views.SendMessage, name='SendMessage'),
    path('seemessage/', views.SeeMessage, name='SeeMessage'), #done
    path('add-product/', views.AddProduct, name='AddProduct'),
    path('delete-product/', views.DeleteProduct, name='DeleteProduct'),
    path('Products/', views.Products, name='Products'),
    path('add-to-cart/', views.AddToCart, name='AddToCart'),
    path('Cart/', views.Cart, name='Cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-view/', views.orderview, name='orderview'),
    path('edit-order-status/<str:order_id>/', views.edit_order_status, name='edit_order_status'),
    path('emergency/', views.emergency, name='emergency'),
]

#C:\Users\AKSHAAY KG\Downloads\ngrok-v3-stable-windows-amd64
#ngrok config add-authtoken 2rIIlksAR0iBQPfbBsyHCq0uXj8_69oW9j3RCoPitMmj6zHt8
#ngrok http 8000
