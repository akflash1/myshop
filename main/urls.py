from django.urls import path
from .views import (ProductList, Register, Login, Logout, ProductCreateView, ProductUpdateView, ProductDeleteView,
                    PurchaseListView,
                    PurchaseCreateView, RefundListView, RefundAgreeView, RefundCreateView, RefundRejectView)

urlpatterns = [

    path('', ProductList.as_view(), name='home'),
    path('register/', Register.as_view(), name='registration'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('products/add/', ProductCreateView.as_view(), name='add_product'),
    path('products/edit/<int:product_id>/', ProductUpdateView.as_view(), name='edit_product'),
    path('product_list/', ProductList.as_view(), name='product_list'),
    path('products/delete/<int:product_id>/', ProductDeleteView.as_view(), name='delete_product'),
    path('products/buy/<int:product_id>/', PurchaseCreateView.as_view(), name='buy_product'),
    path('purchase_list/', PurchaseListView.as_view(), name='purchase_list'),
    path('refunds/', RefundListView.as_view(), name='refunds'),
    path('refund/create/<int:purchase_id>/', RefundCreateView.as_view(), name='create_refund'),
    path('refund_agree/<int:pk>/', RefundAgreeView.as_view(), name='refund_agree'),
    path('refund_reject/<int:pk>/', RefundRejectView.as_view(), name='refund_reject'),
]
