# store/views/customer_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from ..models import Product, Basket, BasketItem
from ..forms import AddToBasketForm

# --- Decorators for role checking ---
def is_customer(user):
    return user.is_authenticated and user.role == 'customer'

customer_login_required = user_passes_test(is_customer, login_url='store:login')

@customer_login_required
def shop_home(request):
    products_with_forms = [] # If using Option 2 from previous filter discussion
    products_qs = Product.objects.filter(stock__gt=0).order_by('name')
    
    # Assuming you are using the custom template filter 'get_item' (Option 1)
    # or the simplified template rendering (Option 3)
    # If using Option 1 (custom filter), the view for product_forms:
    product_forms = {product.id: AddToBasketForm(initial={'product_id': product.id}) for product in products_qs}

    return render(request, 'store/customer/shop_home.html', {
        'products': products_qs, # Pass products for iteration
        'product_forms': product_forms # Pass the dictionary of forms
        })


@customer_login_required
def add_to_basket(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = AddToBasketForm(request.POST, initial={'product_id': product_id})
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            if quantity > product.stock:
                messages.error(request, f"Not enough stock for {product.name}. Only {product.stock} available.")
                return redirect('store:shop_home')

            basket, created = Basket.objects.get_or_create(
                user=request.user,
                status='active'
            )
            
            basket_item, item_created = BasketItem.objects.get_or_create(
                basket=basket,
                product=product,
                defaults={'quantity': 0} 
            )
            
            if not item_created and basket_item.quantity + quantity > product.stock:
                 messages.error(request, f"Adding {quantity} would exceed stock for {product.name}. You have {basket_item.quantity} in basket, {product.stock} available.")
                 return redirect('store:view_basket')

            basket_item.quantity += quantity
            basket_item.save()
            
            messages.success(request, f"{quantity} of {product.name} added to your basket.")
            return redirect('store:view_basket')
        else:
            messages.error(request, "Invalid quantity.")
            return redirect('store:shop_home')
    return redirect('store:shop_home')

@customer_login_required
def view_basket(request):
    try:
        basket = Basket.objects.get(user=request.user, status='active')
    except Basket.DoesNotExist:
        basket = None
    
    return render(request, 'store/customer/view_basket.html', {'basket': basket})

@customer_login_required
def update_basket_item(request, item_id):
    item = get_object_or_404(BasketItem, pk=item_id, basket__user=request.user, basket__status='active')
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        if quantity > 0:
            if quantity > item.product.stock:
                messages.error(request, f"Not enough stock for {item.product.name}. Only {item.product.stock} available.")
            else:
                item.quantity = quantity
                item.save()
                messages.success(request, f"Quantity for {item.product.name} updated.")
        else: 
            item.delete()
            messages.success(request, f"{item.product.name} removed from basket.")
        return redirect('store:view_basket')
    return redirect('store:view_basket')

@customer_login_required
def remove_from_basket(request, item_id):
    item = get_object_or_404(BasketItem, pk=item_id, basket__user=request.user, basket__status='active')
    product_name = item.product.name
    item.delete()
    messages.success(request, f"{product_name} removed from your basket.")
    return redirect('store:view_basket')

@customer_login_required
def submit_basket(request):
    try:
        basket = Basket.objects.get(user=request.user, status='active')
        if not basket.items.exists():
            messages.error(request, "Your basket is empty. Add items before submitting.")
            return redirect('store:view_basket')

        for item in basket.items.all():
            if item.quantity > item.product.stock:
                messages.error(request, f"Not enough stock for {item.product.name}. Only {item.product.stock} available. Please update your basket.")
                return redirect('store:view_basket')
        
        basket.status = 'submitted'
        basket.save()
        messages.success(request, "Your basket has been submitted for processing!")
        return redirect('store:basket_history')
    except Basket.DoesNotExist:
        messages.error(request, "You have no active basket to submit.")
        return redirect('store:shop_home')


@customer_login_required
def basket_history(request):
    baskets = Basket.objects.filter(
        user=request.user
    ).exclude(
        status__in=['active', 'abandoned'] 
    ).prefetch_related( 
        'items__product'
    ).order_by('-updated_at')
    
    # Removed debug print statements that might have been here
    
    return render(request, 'store/customer/basket_history.html', {'baskets': baskets})
