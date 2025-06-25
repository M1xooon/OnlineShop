from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, CartItem, Order, OrderItem, UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    return render(request, 'store/category_detail.html', {
        'category': category,
        'products': products
    })


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('store:cart')


@login_required
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.email = request.POST.get('email')
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        request.user.save()
        profile.save()
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {
        'profile': profile,
        'orders': orders
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('store:home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required(login_url='store:login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


def home(request):
    # Товары из категории SALE
    sale_products = Product.objects.filter(category__name__iexact='Sale')[:10]

    # Популярные товары по количеству заказов
    popular_products = Product.objects.annotate(order_count=Count('orderitem')).order_by('-order_count')[:8]

    return render(request, 'store/home.html', {
        'sale_products': sale_products,
        'popular_products': popular_products
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Размеры — список (можно сохранить в поле или вычислять)
    sizes = product.sizes if hasattr(product, 'sizes') else ['S', 'M', 'L', 'XL']

    # Добавим просмотренный товар в сессию
    recently_viewed = request.session.get('recently_viewed', [])
    if product_id in recently_viewed:
        recently_viewed.remove(product_id)
    recently_viewed.insert(0, product_id)
    if len(recently_viewed) > 5:
        recently_viewed = recently_viewed[:5]
    request.session['recently_viewed'] = recently_viewed

    # Получаем объекты недавно просмотренных товаров (без текущего)
    recently_viewed_products = Product.objects.filter(id__in=recently_viewed).exclude(id=product_id)

    # Похожие товары — из той же категории, кроме текущего
    similar_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:5]

    return render(request, 'store/product_detail.html', {
        'product': product,
        'recently_viewed': recently_viewed_products,
        'similar_products': similar_products,
        'sizes': sizes,
    })


def add_to_cart(request, product_id):
    if request.method == 'POST':
        size = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))
        # Логика добавления в корзину в сессию или в модель Cart
        cart = request.session.get('cart', {})
        key = f'{product_id}_{size}'
        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            cart[key] = {'product_id': product_id, 'size': size, 'quantity': quantity}
        request.session['cart'] = cart
        messages.success(request, 'Товар добавлен в корзину')
        return redirect('store:product_detail', product_id=product_id)
    return redirect('store:home')


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for key, item in cart.items():
        product = Product.objects.get(id=item['product_id'])
        quantity = item['quantity']
        total = product.price * quantity
        total_price += total
        cart_items.append({
            'key': key,
            'product': product,
            'size': item['size'],
            'quantity': quantity,
            'total_price': total,
        })
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total_price': total_price})


def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        keys = list(cart.keys())
        for key in keys:
            qty_key = f'quantity_{key}'
            rem_key = f'remove_{key}'
            if rem_key in request.POST:
                # Удаляем товар
                cart.pop(key, None)
            elif qty_key in request.POST:
                qty = int(request.POST.get(qty_key, 1))
                if qty < 1:
                    qty = 1
                cart[key]['quantity'] = qty
        request.session['cart'] = cart
        messages.success(request, 'Корзина обновлена')
    return redirect('store:cart')


@login_required(login_url='store:login')
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('store:cart')

    # Создаем заказ
    order = Order.objects.create(user=request.user, status='NEW')
    for key, item in cart.items():
        product = Product.objects.get(id=item['product_id'])
        OrderItem.objects.create(
            order=order,
            product=product,
            size=item['size'],
            quantity=item['quantity'],
            price=product.price
        )
    # Очищаем корзину
    request.session['cart'] = {}
    messages.success(request, 'Заказ оформлен')
    return redirect('store:order_detail', order_id=order.id)
