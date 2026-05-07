from sys import path

from django.http import JsonResponse
from django.shortcuts import render,redirect

# Create your views here.
def home(request):
    return render(request, 'home.html')

from .models import *
from django.contrib import messages
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('location')
        phone = request.POST.get('phone')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            User.objects.create(name=name, email=email, password=password, address=address, phone=phone)
            messages.success(request, 'Registration successful!')
            return redirect('home') 
    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email, password=password)
            request.session['email'] = user.email
            return redirect('home')
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid email or password.'}) 
    return render(request, 'login.html')

from django.shortcuts import redirect
 
def logout(request):
    request.session.flush()   # clears all session data including 'email'
    return redirect('home')

## views.py additions — paste these into your views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User  # your custom User model


def profile(request):
    """Show profile page. Requires session login."""
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = User.objects.get(email=email)

    # Cart count — adjust if your Cart model differs
    try:
        from .models import Cart
        cart_count = Cart.objects.filter(user=user).count()
    except Exception:
        cart_count = 0

    # Order count — adjust if your Order model differs
    try:
        from .models import Order
        order_count = Order.objects.filter(user=user).count()
    except Exception:
        order_count = 0

    return render(request, 'profile.html', {
        'user': user,
        'cart_count': cart_count,
        'order_count': order_count,
    })


def edit_profile(request):
    """Handle profile edit POST."""
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = User.objects.get(email=email)

    if request.method == 'POST':
        name     = request.POST.get('name', '').strip()
        phone    = request.POST.get('phone', '').strip()
        address  = request.POST.get('address', '').strip()
        password = request.POST.get('password', '').strip()

        if name:
            user.name = name
        if phone:
            user.phone = phone
        if address:
            user.address = address
        if password:
            user.password = password  # hash in production!

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return redirect('profile')


def userlist(request):
    user=User.objects.all()
    return render(request,'userlist.html',{'user':user})
def deleteuser(request,id):
    data=User.objects.filter(id=id)
    data.delete()
    return redirect('userlist')

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = int(request.POST.get('quantity'))
        category = request.POST.get('category')
        image = request.FILES.get('image')

        # 🔥 Check if product already exists (based on name + category)
        product = Product.objects.filter(name=name, category=category).first()

        if product:
            # ✅ If exists → increase quantity
            product.quantity += quantity

            # Optional: update other fields
            product.price = price
            product.description = description

            # update image only if new uploaded
            if image:
                product.image = image

            product.save()
            messages.success(request, "Product quantity updated!")

        else:
            # ✅ If not exists → create new
            Product.objects.create(
                name=name,
                description=description,
                price=price,
                quantity=quantity,
                category=category,
                image=image
            )
            messages.success(request, "New product added!")

        return redirect('product_list')

    return render(request, 'add_product.html')


def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def edit_product(request, id):
    product = Product.objects.get(id=id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        product.category = request.POST.get('category')

        # update image only if new one uploaded
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('product_list')

    return render(request, 'edit_product.html', {'product': product})

def delete_product(request, id):
    Product.objects.filter(id=id).delete()
    return redirect('product_list')

def update_quantity(request, id, action):
    product = Product.objects.get(id=id)

    if action == 'increase':
        product.quantity += 1
    elif action == 'decrease':
        if product.quantity > 0:
            product.quantity -= 1

    product.save()
    return JsonResponse({'quantity': product.quantity})

def orders(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')
    user = User.objects.get(email=email)
    order_list = Order.objects.filter(user=user).order_by('-id')
    return render(request, 'orders.html', {'orders': order_list})

def checkout(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = User.objects.get(email=email)

    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        product = Product.objects.get(id=product_id)

        total = product.price * quantity

        Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            total_price=total,
            status='Pending'
        )

        return redirect('orders')

    return render(request, 'checkout.html')

def cart(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = User.objects.get(email=email)
    cart_items = Cart.objects.filter(user=user)

    total = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def add_to_cart(request, id):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = User.objects.get(email=email)
    product = Product.objects.get(id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=user,
        product=product
    )

    if not created:
        cart_item.quantity += 1

    cart_item.save()
    return redirect('cart')

def remove_from_cart(request, id):
    Cart.objects.filter(id=id).delete()
    return redirect('cart')

def shop(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})

# ── Admin credentials (hardcoded for simplicity) ──
ADMIN_EMAIL    = 'admin@hotwheels.com'
ADMIN_PASSWORD = 'admin123'

def admin_login(request):
    if request.session.get('is_admin'):
        return redirect('admin_dashboard')
    if request.method == 'POST':
        email    = request.POST.get('email')
        password = request.POST.get('password')
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            request.session['is_admin'] = True
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials.')
    return render(request, 'admin_login.html')

def admin_logout(request):
    request.session.pop('is_admin', None)
    return redirect('admin_login')

def admin_dashboard(request):
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard.html', {'products': products})

def admin_add_product(request):
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    if request.method == 'POST':
        name        = request.POST.get('name')
        description = request.POST.get('description')
        price       = request.POST.get('price')
        quantity    = int(request.POST.get('quantity'))
        category    = request.POST.get('category')
        image       = request.FILES.get('image')
        product = Product.objects.filter(name=name, category=category).first()
        if product:
            product.quantity += quantity
            product.price       = price
            product.description = description
            if image:
                product.image = image
            product.save()
            messages.success(request, 'Product quantity updated!')
        else:
            Product.objects.create(
                name=name, description=description, price=price,
                quantity=quantity, category=category, image=image
            )
            messages.success(request, 'New product added!')
        return redirect('admin_dashboard')
    return render(request, 'admin_add_product.html')

def admin_edit_product(request, id):
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        product.name        = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price       = request.POST.get('price')
        product.quantity    = request.POST.get('quantity')
        product.category    = request.POST.get('category')
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        product.save()
        messages.success(request, 'Product updated!')
        return redirect('admin_dashboard')
    return render(request, 'admin_edit_product.html', {'product': product})


def admin_delete_product(request, id):
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    Product.objects.filter(id=id).delete()
    return redirect('admin_dashboard')

# views.py
from .models import Feedback
from django.contrib import messages

def review_view(request):
    if request.method == 'POST':
        fb = Feedback(
            email=request.POST['email'],
            rating=request.POST['rating'],
            feedback_text=request.POST['feedback_text']
        )
        fb.save()
        messages.success(request, 'Review submitted — thanks for the feedback!')
        return redirect('/review/')
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'review.html', {'feedbacks': feedbacks})


from .models import Feedback
from django.db.models import Avg

def admin_dashboard(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    total = feedbacks.count()
    avg = feedbacks.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg) if avg else None
    five_star_count = feedbacks.filter(rating=5).count()

    # Rating breakdown with percentages
    breakdown = []
    for r in range(5, 0, -1):
        cnt = feedbacks.filter(rating=r).count()
        breakdown.append({
            'rating': r,
            'count': cnt,
            'pct': round((cnt / total * 100) if total else 0)
        })

    return render(request, 'admin_dashboard.html', {
        'products': Product.objects.all(),
        'feedbacks': feedbacks,
        'avg_rating': avg_rating,
        'five_star_count': five_star_count,
        'rating_breakdown': breakdown,
    })
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Feedback

def delete_review(request, pk):
    review = get_object_or_404(Feedback, pk=pk)
    review.delete()
    messages.success(request, 'Review deleted successfully.')
    return redirect('admin_dashboard')
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from groq import Groq
from dotenv import load_dotenv

import json
import os

# Load .env file
load_dotenv()

# Read API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@csrf_exempt
def chatbot(request):

    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert assistant for a Hot Wheels website. "
                            "You ONLY answer questions related to Hot Wheels cars, die-cast models, "
                            "car brands, automotive topics, racing, and vehicle-related subjects. "
                            "If a user asks anything unrelated, politely refuse and say: "
                            "'I can only help with Hot Wheels and car-related topics.'"
                        )
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                temperature=0.7,
                max_completion_tokens=512,
            )

            reply = completion.choices[0].message.content

            return JsonResponse({"response": reply})

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return render(request, "chatbot.html")

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        email = request.session.get('email')
        if not email:
            return JsonResponse({'success': False, 'message': 'Not logged in'})

        try:
            user = User.objects.get(email=email)
            data = json.loads(request.body)
            items = data.get('items', [])

            if not items:
                return JsonResponse({'success': False, 'message': 'Cart is empty'})

            last_order = None
            for item in items:
                product = Product.objects.get(id=item['id'])
                quantity = int(item.get('qty') or item.get('quantity', 1))  # ← fixed
                total = int(product.price * quantity)                        # ← int() for IntegerField
                last_order = Order.objects.create(
                    user=user,
                    product=product,
                    quantity=quantity,
                    total_price=total,
                    status='Pending'
                )

            return JsonResponse({'success': True, 'order_id': last_order.id})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request'})