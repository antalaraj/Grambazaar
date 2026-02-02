from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import timedelta
import csv
from io import StringIO
from django.utils.text import slugify

from .models import SHG, Product, Order, DigiCourse, DigiProgress, ForecastNotification, LedgerEntry, BuyerProfile, ProductReview
from .forms import SHGRegistrationForm, ProductSubmissionForm, BuyerOrderForm, LoginForm, AdminProductForm, BuyerRegistrationForm, BuyerLoginForm, UserUpdateForm, BuyerProfileForm, DigiCourseForm, ProductReviewForm


def _user_is_admin(user):
    return user.is_authenticated and user.username == 'Admin'


@login_required
def admin_delete_product(request, product_id):
    """Delete a product from admin panel"""
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to delete products.')
        return redirect('market:login')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = product.title
        product.delete()
        messages.success(request, f'Product "{product_name}" has been deleted successfully.')
        return redirect('market:admin_dashboard')
    
    return render(request, 'market/admin_delete_product.html', {'product': product})


def home(request):
    featured_products = Product.objects.filter(status='live')[:6]
    return render(request, 'market/home.html', {'featured_products': featured_products})


def marketplace(request):
    products = Product.objects.filter(status='live').order_by('-created_at')
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category=category_filter)
    
    return render(request, 'market/marketplace.html', {
        'products': products,
        'category_filter': category_filter
    })


def contact_us(request):
    return render(request, 'market/contact.html')


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, status='live')
    reviews = ProductReview.objects.filter(product=product).select_related('user')
    review_form = None

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please login as a buyer to submit a review.')
            return redirect('market:buyer_login')

        review_form = ProductReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('market:product_detail', slug=product.slug)
    else:
        if request.user.is_authenticated:
            review_form = ProductReviewForm()

    return render(request, 'market/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
    })


def shg_signup(request):
    if request.method == 'POST':
        form = SHGRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            
            user = User.objects.create_user(username=username, password=password, email=email)
            shg = form.save(commit=False)
            shg.user = user
            shg.save()
            
            login(request, user)
            messages.success(request, 'SHG registration successful!')
            return redirect('market:shg_dashboard')
    else:
        form = SHGRegistrationForm()
    
    return render(request, 'market/signup_shg.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                
                try:
                    shg = user.shg
                    return redirect('market:shg_dashboard')
                except SHG.DoesNotExist:
                    return redirect('market:admin_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    
    return render(request, 'market/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('market:home')


@login_required
def shg_dashboard(request):
    try:
        shg = request.user.shg
    except SHG.DoesNotExist:
        return redirect('market:admin_dashboard')
    
    products = Product.objects.filter(shg=shg).order_by('-created_at')
    courses = DigiCourse.objects.all()
    notifications = ForecastNotification.objects.filter(
        target_shgs=shg
    ).exclude(read_by=shg).order_by('-created_at')[:5]

    delivery_orders = (
        Order.objects.filter(product__shg=shg, status='approved')
        .select_related('product')
        .order_by('-created_at')[:5]
    )
    
    return render(request, 'market/shg_dashboard.html', {
        'shg': shg,
        'products': products,
        'courses': courses,
        'notifications': notifications,
        'delivery_orders': delivery_orders,
    })


@login_required
def submit_product(request):
    try:
        shg = request.user.shg
    except SHG.DoesNotExist:
        return redirect('market:admin_dashboard')
    
    if request.method == 'POST':
        form = ProductSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(shg=shg)
            messages.success(request, 'Product submitted for approval!')
            return redirect('market:shg_dashboard')
    else:
        form = ProductSubmissionForm()
    
    return render(request, 'market/submit_product.html', {'form': form})


@login_required
def request_product_removal(request, product_id):
    """Allow an SHG to request removal of their product."""
    try:
        shg = request.user.shg
    except SHG.DoesNotExist:
        messages.error(request, 'Only SHGs can request product removal.')
        return redirect('market:login')

    product = get_object_or_404(Product, id=product_id, shg=shg)

    # Only allow removal requests for live or pending products that are not already requested
    if product.removal_requested:
        messages.info(request, f'Removal already requested for "{product.title}".')
        return redirect('market:shg_dashboard')

    if product.status not in ['live', 'pending']:
        messages.error(request, 'Removal can only be requested for live or pending products.')
        return redirect('market:shg_dashboard')

    product.removal_requested = True
    product.save(update_fields=['removal_requested'])
    messages.success(request, f'Removal request submitted for "{product.title}".')
    return redirect('market:shg_dashboard')


@login_required
def shg_wallet(request):
    try:
        shg = request.user.shg
    except SHG.DoesNotExist:
        return redirect('admin_dashboard')
    
    ledger_entries = LedgerEntry.objects.filter(shg=shg).order_by('-date')
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="ledger_{shg.name}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Description', 'Credit', 'Debit', 'Balance After'])
        
        for entry in ledger_entries:
            writer.writerow([
                entry.date, entry.description, 
                entry.credit, entry.debit, entry.balance_after
            ])
        
        return response
    
    return render(request, 'market/shg_wallet.html', {
        'shg': shg,
        'ledger_entries': ledger_entries
    })


@login_required
def shg_wallet_api(request):
    try:
        shg = request.user.shg
    except SHG.DoesNotExist:
        return JsonResponse({'error': 'forbidden'}, status=403)
    
    ledger_entries = LedgerEntry.objects.filter(shg=shg).order_by('-date', '-id')
    data = {
        'balance': str(shg.wallet_balance),
        'entries': []
    }

    for entry in ledger_entries:
        data['entries'].append({
            'date': entry.date.strftime('%Y-%m-%d'),
            'description': entry.description,
            'credit': float(entry.credit) if entry.credit else None,
            'debit': float(entry.debit) if entry.debit else None,
            'balance_after': str(entry.balance_after),
        })

    return JsonResponse(data)


@login_required
def admin_dashboard(request):
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    try:
        request.user.shg
        return redirect('market:shg_dashboard')
    except SHG.DoesNotExist:
        pass
    
    shg_count = SHG.objects.count()
    product_count = Product.objects.count()
    pending_products = Product.objects.filter(status='pending').count()
    pending_orders = Order.objects.filter(status='pending_admin_approval').count()
    live_products = Product.objects.filter(status='live').select_related('shg').order_by('-created_at')[:20]
    recent_reviews = ProductReview.objects.select_related('product', 'user').order_by('-created_at')[:8]
    
    context = {
        'shg_count': shg_count,
        'product_count': product_count,
        'pending_products': pending_products,
        'pending_orders': pending_orders,
        'live_products': live_products,
        'recent_reviews': recent_reviews,
    }
    
    return render(request, 'market/admin_dashboard.html', context)


@login_required
def admin_add_product(request):
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    if request.method == 'POST':
        form = AdminProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            # Auto-generate slug from title and SHG name
            product.slug = slugify(f"{product.title}-{product.shg.name}")
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('market:admin_dashboard')
    else:
        form = AdminProductForm()

    return render(request, 'market/admin_add_product.html', {'form': form})


@login_required
def admin_edit_product(request, product_id):
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = AdminProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            # Keep slug in sync with title and SHG
            product.slug = slugify(f"{product.title}-{product.shg.name}")
            product.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('market:admin_dashboard')
    else:
        form = AdminProductForm(instance=product)

    return render(request, 'market/admin_add_product.html', {
        'form': form,
        'product': product,
        'editing': True,
    })


@login_required
def admin_pending_products(request):
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    try:
        request.user.shg
        return redirect('market:shg_dashboard')
    except SHG.DoesNotExist:
        pass
    
    pending_products = Product.objects.filter(
        Q(status='pending') | Q(removal_requested=True)
    ).order_by('-created_at')
    return render(request, 'market/admin_pending_products.html', {
        'pending_products': pending_products
    })


@login_required
def approve_product(request, product_id):
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    try:
        request.user.shg
        return redirect('market:shg_dashboard')
    except SHG.DoesNotExist:
        pass
    
    product = get_object_or_404(Product, id=product_id)
    product.status = 'live'
    product.save()
    
    messages.success(request, f'Product "{product.title}" approved!')
    return redirect('market:admin_pending_products')


@login_required
def approve_removal(request, product_id):
    """Admin approves SHG product removal request."""
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    try:
        request.user.shg
        return redirect('market:shg_dashboard')
    except SHG.DoesNotExist:
        pass

    product = get_object_or_404(Product, id=product_id, removal_requested=True)
    title = product.title
    product.delete()
    messages.success(request, f'Product "{title}" removed.')
    return redirect('market:admin_pending_products')


@login_required
def reject_product(request, product_id):
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    try:
        request.user.shg
        return redirect('market:shg_dashboard')
    except SHG.DoesNotExist:
        pass
    
    product = get_object_or_404(Product, id=product_id)
    product.status = 'rejected'
    product.save()
    
    messages.success(request, f'Product "{product.title}" rejected!')
    return redirect('market:admin_pending_products')


@login_required
def reject_removal(request, product_id):
    """Admin rejects SHG product removal request."""
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    try:
        request.user.shg
        return redirect('market:shg_dashboard')
    except SHG.DoesNotExist:
        pass

    product = get_object_or_404(Product, id=product_id, removal_requested=True)
    product.removal_requested = False
    product.save(update_fields=['removal_requested'])
    messages.success(request, f'Removal request for "{product.title}" rejected.')
    return redirect('market:admin_pending_products')


@login_required
def admin_orders(request):
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    try:
        request.user.shg
        return redirect('market:shg_dashboard')
    except SHG.DoesNotExist:
        pass
    
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'market/admin_orders.html', {'orders': orders})


@login_required
def admin_digicourses(request):
    """Admin management page for DigiTutor / DigiLearner courses."""
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    if request.method == 'POST':
        form = DigiCourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'DigiTutor course added successfully.')
            return redirect('market:admin_digicourses')
    else:
        form = DigiCourseForm()

    courses = DigiCourse.objects.all().order_by('-created_at')
    return render(request, 'market/admin_digicourses.html', {
        'form': form,
        'courses': courses,
    })


@login_required
def admin_delete_digicourse(request, course_id):
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    course = get_object_or_404(DigiCourse, id=course_id)

    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f'Course "{title}" deleted successfully.')
        return redirect('market:admin_digicourses')

    return render(request, 'market/admin_delete_digicourse.html', {
        'course': course,
    })


@login_required
def approve_order(request, order_id):
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    try:
        request.user.shg
        return redirect('market:shg_dashboard')
    except SHG.DoesNotExist:
        pass
    
    order = get_object_or_404(Order, id=order_id)
    order.status = 'approved'
    order.save()
    
    messages.success(request, f'Order {order.id} approved!')
    return redirect('market:admin_orders')


@login_required
def buyer_order(request, slug):
    product = get_object_or_404(Product, slug=slug, status='live')
    
    # Check if product is in stock
    if product.inventory <= 0:
        messages.error(request, 'Sorry, this product is out of stock.')
        return redirect('market:product_detail', slug=slug)
    
    if request.method == 'POST':
        form = BuyerOrderForm(request.POST)
        if form.is_valid():
            # Double-check inventory before proceeding to payment
            if product.inventory <= 0:
                messages.error(request, 'Sorry, this product is now out of stock.')
                return redirect('market:product_detail', slug=slug)

            # Store pending order details in session and redirect to fake payment page
            request.session['pending_order'] = {
                'product_id': product.id,
                'buyer_name': form.cleaned_data.get('buyer_name'),
                'buyer_contact': form.cleaned_data.get('buyer_contact'),
                'address': form.cleaned_data.get('address'),
            }
            return redirect('market:fake_payment', slug=slug)
    else:
        # Pre-fill form with buyer's information if available
        initial = {
            'buyer_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        }
        
        try:
            buyer_profile = request.user.buyerprofile
            initial.update({
                'buyer_contact': buyer_profile.phone,
                'address': buyer_profile.address
            })
        except BuyerProfile.DoesNotExist:
            pass
            
        form = BuyerOrderForm(initial=initial)
    
    return render(request, 'market/buyer_order.html', {
        'product': product,
        'form': form
    })


@login_required
def fake_payment(request, slug):
    product = get_object_or_404(Product, slug=slug, status='live')

    pending = request.session.get('pending_order')
    if not pending or pending.get('product_id') != product.id:
        messages.error(request, 'Your payment session has expired. Please place the order again.')
        return redirect('market:buyer_order', slug=slug)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method') or 'card'
        method_label = {
            'card': 'Card',
            'upi': 'UPI',
            'cod': 'Cash on Delivery',
        }.get(payment_method, 'Card')

        # Final inventory check before creating order
        if product.inventory <= 0:
            messages.error(request, 'Sorry, this product is now out of stock.')
            request.session.pop('pending_order', None)
            return redirect('market:product_detail', slug=slug)

        order = Order.objects.create(
            product=product,
            amount=product.price,
            buyer_name=pending.get('buyer_name') or (f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username),
            buyer_contact=pending.get('buyer_contact') or '',
            address=pending.get('address') or '',
            status='pending_admin_approval',
        )

        # Update inventory
        product.inventory -= 1
        product.save()

        # Add ledger entry for SHG (will be credited after approval)
        LedgerEntry.objects.create(
            shg=product.shg,
            date=timezone.now().date(),
            description=f"Order #{order.id} - {product.title} ({method_label}, Pending)",
            credit=0,
            debit=0,
            balance_after=product.shg.wallet_balance
        )

        request.session.pop('pending_order', None)
        messages.success(request, 'Payment successful! Your order has been placed and is pending approval.')
        return redirect('market:my_orders')

    return render(request, 'market/fake_payment.html', {
        'product': product,
        'pending': pending,
    })


def instabrand_api(request):
    if request.method == 'POST':
        image_url = request.POST.get('image_url', '')
        category = request.POST.get('category', '')
        shg_id = request.POST.get('shg_id', '')
        
        response_data = {
            "title": "Handmade Cotton Bag",
            "description": "Crafted by SHG artisans with love and care.",
            "hashtags": "#handmade #SHG #GramBazaar #sustainable",
            "poster_url": "/static/sample_poster.jpg"
        }
        
        return JsonResponse(response_data)
    
    return render(request, 'market/instabrand.html')


def notifications_poll(request):
    try:
        shg = request.user.shg
    except SHG.DoesNotExist:
        return JsonResponse({'notifications': []})
    
    notifications = ForecastNotification.objects.filter(
        Q(target_shgs=shg) | Q(target_shgs__isnull=True)
    ).exclude(read_by=shg).order_by('-created_at')[:5]
    
    data = []
    for notif in notifications:
        data.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'created_at': notif.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({'notifications': data})


@login_required
def mark_notification_read(request, notif_id):
    try:
        shg = request.user.shg
    except SHG.DoesNotExist:
        return JsonResponse({'success': False})
    
    notification = get_object_or_404(ForecastNotification, id=notif_id)
    notification.read_by.add(shg)
    
    return JsonResponse({'success': True})


@login_required
def generate_forecast(request):
    if not _user_is_admin(request.user):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('market:login')

    try:
        request.user.shg
        return redirect('market:shg_dashboard')
    except SHG.DoesNotExist:
        pass

    products = Product.objects.filter(status='live').order_by('title')
    selected_product = None
    product_id = request.GET.get('product')
    if product_id:
        try:
            selected_product = products.get(id=product_id)
        except Product.DoesNotExist:
            selected_product = None
    
    forecasts = _build_forecasts(create_notifications=True, filter_product=selected_product)
    analytics = _build_forecast_analytics(filter_product=selected_product)

    return render(request, 'market/admin_forecast.html', {
        'forecasts': forecasts,
        'analytics': analytics,
        'products': products,
        'selected_product': selected_product,
    })


def _build_forecasts(create_notifications=False, filter_product=None):
    forecasts = []

    products = Product.objects.filter(status='live').select_related('shg')
    if filter_product is not None:
        products = products.filter(id=filter_product.id)

    # Rule 1: low inventory
    for product in products:
        if product.inventory < 5:
            message = _(
                'Low inventory for %(product_title)s! Only %(inventory)s items left. '
                'We recommend increasing production.'
            ) % {
                'product_title': product.title,
                'inventory': product.inventory,
            }
            forecasts.append({
                'product': product.title,
                'shg': product.shg.name,
                'message': message,
                'priority': 'high',
            })

            if create_notifications:
                notif = ForecastNotification.objects.create(
                    title='Low Inventory Alert',
                    message=message,
                )
                notif.target_shgs.add(product.shg)

    # Rule 2: seasonal boost for food products
    for product in products.filter(category='food'):
        message = _(
            'Seasonal demand expected for %(product_title)s around festival periods. '
            'Plan extra stock and promotions.'
        ) % {
            'product_title': product.title,
        }
        forecasts.append({
            'product': product.title,
            'shg': product.shg.name,
            'message': message,
            'priority': 'medium',
        })

        if create_notifications:
            notif = ForecastNotification.objects.create(
                title='Seasonal Demand Insight',
                message=message,
            )
            notif.target_shgs.add(product.shg)

    return forecasts


def _build_forecast_analytics(filter_product=None):
    now = timezone.now()
    recent_start = now - timedelta(days=30)
    prev_start = now - timedelta(days=60)

    completed_statuses = ['approved', 'shipped', 'delivered']

    recent_orders = Order.objects.filter(
        status__in=completed_statuses,
        created_at__gte=recent_start,
    )

    prev_orders = Order.objects.filter(
        status__in=completed_statuses,
        created_at__lt=recent_start,
        created_at__gte=prev_start,
    )

    if filter_product is not None:
        recent_orders = recent_orders.filter(product=filter_product)
        prev_orders = prev_orders.filter(product=filter_product)

    recent_count = recent_orders.count()
    prev_count = prev_orders.count()

    if prev_count == 0:
        if recent_count == 0:
            trend_direction = 'stable'
            trend_change_pct = 0
        else:
            trend_direction = 'up'
            trend_change_pct = 100
    else:
        diff = recent_count - prev_count
        trend_change_pct = int(round((diff / prev_count) * 100))
        if diff > 0:
            trend_direction = 'up'
        elif diff < 0:
            trend_direction = 'down'
        else:
            trend_direction = 'stable'

    def extract_area(address):
        if not address:
            return 'Unknown'
        parts = [p.strip() for p in address.split(',') if p.strip()]
        if not parts:
            return 'Unknown'
        if len(parts) >= 2:
            return parts[-2]
        return parts[-1]

    area_counts = {}
    for order in recent_orders:
        area = extract_area(order.address)
        area_counts[area] = area_counts.get(area, 0) + 1

    top_areas = [
        {'area': area, 'orders': count}
        for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    product_area_map = {}
    for order in recent_orders.select_related('product'):
        product_title = order.product.title
        area = extract_area(order.address)
        if product_title not in product_area_map:
            product_area_map[product_title] = {}
        product_area_map[product_title][area] = product_area_map[product_title].get(area, 0) + 1

    product_heatmap = []
    for product_title, areas in product_area_map.items():
        sorted_areas = sorted(areas.items(), key=lambda x: x[1], reverse=True)[:5]
        product_heatmap.append({
            'product': product_title,
            'areas': [
                {'area': a, 'orders': c}
                for a, c in sorted_areas
            ],
        })

    product_heatmap.sort(key=lambda item: sum(a['orders'] for a in item['areas']), reverse=True)

    return {
        'sales_trend': {
            'recent_orders': recent_count,
            'previous_orders': prev_count,
            'direction': trend_direction,
            'change_pct': trend_change_pct,
        },
        'top_areas': top_areas,
        'product_heatmap': product_heatmap,
    }


@login_required
def admin_forecast_api(request):
    if not _user_is_admin(request.user):
        return JsonResponse({'error': 'forbidden'}, status=403)

    try:
        request.user.shg
        return JsonResponse({'error': 'forbidden'}, status=403)
    except SHG.DoesNotExist:
        pass

    forecasts = _build_forecasts(create_notifications=False)
    analytics = _build_forecast_analytics()

    return JsonResponse({'forecasts': forecasts, 'analytics': analytics})


@login_required
def shg_forecast_view(request):
    try:
        shg = request.user.shg
    except SHG.DoesNotExist:
        return redirect('market:admin_dashboard')

    products = Product.objects.filter(status='live').order_by('title')
    selected_product = None
    product_id = request.GET.get('product')
    if product_id:
        try:
            selected_product = products.get(id=product_id)
        except Product.DoesNotExist:
            selected_product = None

    forecasts = _build_forecasts(create_notifications=False, filter_product=selected_product)
    analytics = _build_forecast_analytics(filter_product=selected_product)

    return render(request, 'market/admin_forecast.html', {
        'forecasts': forecasts,
        'analytics': analytics,
        'products': products,
        'selected_product': selected_product,
        'is_shg_view': True,
    })


def buyer_register(request):
    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.save()
            
            # Create buyer profile
            BuyerProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                pincode=form.cleaned_data['pincode']
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('market:home')
    else:
        form = BuyerRegistrationForm()
    return render(request, 'market/buyer/register.html', {'form': form})


def buyer_login_view(request):
    if request.method == 'POST':
        form = BuyerLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('market:home')
    else:
        form = BuyerLoginForm()
    return render(request, 'market/buyer/login.html', {'form': form})


@login_required
def buyer_profile(request):
    try:
        profile = request.user.buyerprofile
    except BuyerProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = BuyerProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = BuyerProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('market:buyer_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = BuyerProfileForm(instance=profile)
    
    return render(request, 'market/buyer/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def buyer_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('market:home')


@login_required
def my_orders(request):
    # Get orders where the buyer's name matches the logged-in user's name
    orders = Order.objects.filter(
        buyer_name__iexact=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    ).order_by('-created_at')
    
    return render(request, 'market/buyer/orders.html', {
        'orders': orders
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Verify the order belongs to the current user
    if not (order.buyer_name == f"{request.user.first_name} {request.user.last_name}".strip() or 
            order.buyer_name == request.user.username):
        raise Http404("Order not found")
    
    return render(request, 'market/buyer/order_detail.html', {
        'order': order
    })


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Verify the order belongs to the current user (same logic as order_detail)
    expected_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    if order.buyer_name.lower() != expected_name.lower():
        raise Http404("Order not found")

    if order.status != 'pending_admin_approval':
        messages.error(request, 'This order can no longer be cancelled.')
        return redirect('market:my_orders')

    if request.method == 'POST':
        # Mark as cancelled
        order.status = 'cancelled'
        order.save()

        # Restore product inventory
        product = order.product
        product.inventory += 1
        product.save()

        # Optional ledger note for transparency
        LedgerEntry.objects.create(
            shg=product.shg,
            date=timezone.now().date(),
            description=f"Order #{order.id} - {product.title} (Cancelled by buyer)",
            credit=0,
            debit=0,
            balance_after=product.shg.wallet_balance
        )

        messages.success(request, 'Your order has been cancelled.')
        return redirect('market:my_orders')

    # For safety, only allow POST; GET just redirects
    return redirect('market:my_orders')
