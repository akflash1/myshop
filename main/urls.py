from django.urls import path
from .views import (ProductList, Register, Login, Logout, AddProduct, EditProduct, DeleteProduct, PurchaseList,
                    BuyProduct)

urlpatterns = [

    path('', ProductList.as_view(), name='home'),
    path('register/', Register.as_view(), name='registration'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('products/add/', AddProduct.as_view(), name='add_product'),
    path('products/edit/<int:product_id>/', EditProduct.as_view(), name='edit_product'),
    path('product_list/', ProductList.as_view(), name='product_list'),
    path('products/delete/<int:product_id>/', DeleteProduct.as_view(), name='delete_product'),
    path('products/buy/<int:product_id>/', BuyProduct.as_view(), name='buy_product'),
    path('purchase_list/', PurchaseList.as_view(), name='purchase_list'),
]
