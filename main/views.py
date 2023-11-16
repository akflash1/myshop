from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .forms import ProductForm, RefundForm, PurchaseForm, UserCreateForm
from django.shortcuts import get_object_or_404
from .models import Product, Purchase, Refund


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseRedirect('login/')


class RefundCreateView(LoginRequiredMixin, CreateView):
    model = Refund
    form_class = RefundForm
    success_url = reverse_lazy('purchase_list')

    def get_success_url(self):
        return self.success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'purchase_id': self.kwargs['purchase_id'],
            'request': self.request,
        })
        return kwargs

    def form_invalid(self, form):
        return HttpResponseRedirect(self.success_url)


class RefundListView(AdminRequiredMixin, ListView):
    model = Refund
    template_name = 'main/refund/refund_list.html'


class RefundAgreeView(AdminRequiredMixin, DeleteView):
    template_name = 'main/refund/confirm_refund.html'
    model = Refund
    success_url = reverse_lazy('refunds')

    def form_valid(self, form):
        if self.object:
            self.object.refund_purchase.product.stock += self.object.refund_purchase.quantity
            self.object.refund_purchase.user.wallet += self.object.refund_purchase.quantity * self.object.refund_purchase.product.price

            with transaction.atomic():
                self.object.refund_purchase.product.save()
                self.object.refund_purchase.user.save()
                self.object.refund_purchase.delete()

        return super().form_valid(form=form)


class RefundRejectView(AdminRequiredMixin, DeleteView):
    model = Refund
    success_url = reverse_lazy('refunds')


class PurchaseCreateView(LoginRequiredMixin, CreateView):
    model = Purchase
    success_url = reverse_lazy('product_list')
    form_class = PurchaseForm
    login_url = 'login/'
    http_method_names = ['post']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'product': get_object_or_404(Product, id=self.kwargs['product_id']),
            'user': self.request.user
        })
        return kwargs

    def form_valid(self, form):
        purchase = form.save(commit=False)
        purchase.product = form.product
        purchase.user = form.user

        total_price = form.product.price * form.cleaned_data['quantity']
        form.user.wallet -= total_price
        form.product.stock -= form.cleaned_data['quantity']

        with transaction.atomic():
            self.request.user.save()
            purchase.save()
            form.product.save()

        return super().form_valid(form=form)

    def form_invalid(self, form):
        return HttpResponseRedirect(self.success_url)


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'main/purchase/purchase_list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)


class ProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('product_list')


class ProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'main/product/edit_product.html'
    success_url = reverse_lazy('product_list')


class ProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'main/product/add_product.html'
    success_url = reverse_lazy('product_list')


class ProductList(ListView):
    model = Product
    template_name = 'main/product/product_list.html'
    context_object_name = 'products'
    extra_context = {'purchase_form': PurchaseForm()}


class Login(LoginView):
    template_name = 'main/user/login.html'
    success_url = '/'
    next_page = 'home'


class Logout(LogoutView):
    next_page = 'home'


class Register(CreateView):
    template_name = 'main/user/register.html'
    success_url = reverse_lazy('home')
    form_class = UserCreateForm
