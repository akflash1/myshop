from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView
from .forms import UserCreationForm, ProductForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Purchase

@method_decorator(login_required, name='dispatch')
class BuyProduct(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity'))

        if product.stock < quantity:
            return render(request, 'main/product/product_list.html', {'eror_message': 'Not enough items in stock.'})
        if request.user.wallet < product.price * quantity:
            return render(request, 'main/product/product_list.html', {'error_message': "You don't have enough money."})

        Purchase.objects.create(user=request.user, product=product, quantity=quantity)

        product.stock -= quantity
        product.save()

        request.user.wallet -= product.price * quantity
        request.user.save()

        return redirect('product_list')

class PurchaseList(ListView):
    model = Purchase
    template_name = 'main/purchase/purchase_list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)


@method_decorator(login_required, name='dispatch')
class DeleteProduct(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        product.delete()
        return redirect('product_list')

@method_decorator(login_required, name='dispatch')
class EditProduct(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(instance=product)
        return render(request, 'main/product/edit_product.html', {'form': form})

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
        return render(request, 'main/product/edit_product.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class AddProduct(View):
    def get(self, request):
        form = ProductForm()
        return render(request, 'main/product/add_product.html', {'form': form})

    def post(self, request):
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
        return render(request, 'main/product/add_product.html', {'form': form})


class ProductList(ListView):
    model = Product
    template_name = 'main/product/product_list.html'
    context_object_name = 'products'


class Login(LoginView):
    template_name = 'main/user/login.html'
    success_url = '.'
    next_page = 'home'

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)


class Logout(LogoutView):
    next_page = 'home'


class Register(FormView):
    template_name = 'main/user/register.html'
    form_class = UserCreationForm
    success_url = 'home'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)
