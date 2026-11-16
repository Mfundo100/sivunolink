import csv
import random
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.utils import timezone
from django.utils.crypto import get_random_string

# Update this line to include your new models!
from .models import (
    Order, OrderItem, ProduceListing, User, EscrowTransaction, AuditLog, 
    OTPRecord, PlatformSetting, OrderFulfilment, PaymentTransaction
)
from .decorators import role_required
from .forms import BuyerSignUpForm

# --- LIGHTWEIGHT I18N DICTIONARY ---
LANG_DICT = {
    'en': {
        'title': 'Buyer Dashboard', 'welcome': 'Welcome back! Browse the marketplace below.',
        'secure': 'Secure in Escrow', 'dispute': 'Open Dispute', 'marketplace': 'Marketplace', 'cart': 'Cart',
        'admin_title': 'Platform Administration', 'user_mgmt': 'User Management', 'recent_actions': 'Recent Platform Actions',
        'user': 'User', 'role': 'Role', 'status': 'Status', 'actions': 'Actions', 'toggle': 'Toggle Status', 'active': 'Active', 'suspended': 'Suspended',
        'driver_title': 'Driver Logistics Hub', 'driver_welcome': 'Manage your active deliveries here.',
        'active_delivery': 'Active Delivery:', 'buyer_label': 'Buyer:', 'pickup_label': 'PICKUP', 'dest_label': 'DESTINATION',
        'verify_delivery': 'Verify Delivery & Release Funds', 'pin_instructions': 'Enter Order Number and PIN to unlock Escrow.',
        'confirm_release': 'Confirm & Release', 'no_deliveries': 'No Active Deliveries', 
        'pin_success': 'Funds released successfully!', 'pin_error': 'Invalid Order ID or PIN.',
        'landing_headline_1': "Connecting Eswatini's", 'landing_headline_2': "Farmers", 'landing_headline_3': "to the", 'landing_headline_4': "Market",
        'landing_sub': "The secure digital bridge between rural agriculture and urban commerce.",
        'landing_btn_login': "Log In", 'landing_btn_register': "Register",
        'admin_hub_title': 'Administrator Dashboard', 'card_users': 'User Management', 'card_assign': 'Driver Assignment', 
        'card_approvals': 'Account Approvals', 'card_monitor': 'Delivery Monitoring', 'card_reports': 'Reports & Analytics',
        'btn_manage': 'Manage Users', 'btn_assign': 'Assign Drivers', 'btn_review': 'Review Accounts', 'btn_reports': 'View Reports', 'btn_monitor': 'Monitor Deliveries', 'btn_back': 'Back to Hub',
        'add_to_cart': 'Add to Cart', 'cart_empty': 'Your cart is empty.', 'cart_empty_sub': 'Browse the marketplace to add fresh produce.',
        'continue_shopping': 'Continue Shopping', 'proceed_checkout': 'Proceed to Checkout',
        'checkout_title': 'Checkout', 'order_summary': 'Order Summary', 'total': 'Total', 'payment_method': 'Select Payment Method',
        'confirm_order': 'Confirm Order', 'order_success': 'Order Placed Successfully!', 'order_id': 'Order Number', 'pin': '4-Digit PIN',
         'my_fulfilments': 'My Order Fulfilments',
        'gross_amount': 'Gross Amount',
        'platform_fee': 'Platform Fee',
        'net_payout': 'Net Payout',
        'status_confirmed': 'CONFIRMED',
        'status_completed': 'COMPLETED',
        'btn_mark_completed': 'Mark as Dispatched / Completed',
        'no_fulfilments': 'No active fulfilments at the moment.',
        'dashboard_btn': 'Go to Dashboard'
    },
    'sz': {
        'title': 'Ikhasi Lephasi', 'welcome': 'Siyakwamukela! Buka imakethe ngezansi.',
        'my_fulfilments': 'Kugcwaliseka Kwema-oda Ami',
        'gross_amount': 'Imali Iyonkhe',
        'platform_fee': 'Inkokhelo ye-Platform',
        'net_payout': 'Imali Lekhishwako',
        'status_confirmed': 'KUCINISEKISIWE',
        'status_completed': 'KUCOTJIWE',
        'btn_mark_completed': 'Phawula Kutsi Sekucotjiwe',
        'no_fulfilments': 'Akukho kugcwaliseka kwema-oda nyalo.',
        'secure': 'Vikela ku-Escrow', 'dispute': 'Vula Ingxabano', 'marketplace': 'Imakethe', 'cart': 'Ikalishi',
        'admin_title': 'Kuphatsa Iphulatifomu', 'user_mgmt': 'Kuphatsa Basebenti', 'recent_actions': 'Tento Tekugcina',
        'user': 'Umsebenti', 'role': 'Indzima', 'status': 'Simo', 'actions': 'Tento', 'toggle': 'Shintja Simo', 'active': 'Kusebenta', 'suspended': 'Kumisiwe',
        'driver_title': 'Ikhasi Labashayeli', 'driver_welcome': 'Phatsa tindzaba tekuhamba kwakho lapha.',
        'active_delivery': 'Kuhamba Lokusebentako:', 'buyer_label': 'Umtsengi:', 'pickup_label': 'LAPHO KUKHETSWA', 'dest_label': 'LAPHO KUHAMBA',
        'verify_delivery': 'Cinisekisa Kuhamba & Khipha Imali', 'pin_instructions': 'Faka i-oda ne-PIN kute uvule i-Escrow.',
        'confirm_release': 'Cinisekisa & Khipha', 'no_deliveries': 'Akukho Kuhamba Lokusebentako', 
        'pin_success': 'Imali ikhishwe ngekuphumelela!', 'pin_error': 'I-oda noma i-PIN ayilungile.',
        'landing_headline_1': "Kuxhumanisa", 'landing_headline_2': "Batsengisi", 'landing_headline_3': "base-Eswatini", 'landing_headline_4': "Nemakethe",
        'landing_sub': "SivunoLink iyibhuloho lephephile ledijithali emkhatsini wetekulima kwemaphandza netekuhweba emadolobheni.",
        'landing_btn_login': "Ngena", 'landing_btn_register': "Bhalisa",
        'admin_hub_title': 'Ikhasi Leliphathi', 'card_users': 'Kuphatsa Basebenti', 'card_assign': 'Kwabela Bashayeli', 
        'card_approvals': 'Kuvuma Ama-Akhawunti', 'card_monitor': 'Kubuka Kuhamba', 'card_reports': 'Imibiko & Tihlatiyelo',
        'btn_manage': 'Phatsa Basebenti', 'btn_assign': 'Yabela Bashayeli', 'btn_review': 'Buka Ama-Akhwunti', 'btn_reports': 'Buka Imibiko', 'btn_monitor': 'Buka Kuhamba', 'btn_back': 'Buyela Emuva',
        'add_to_cart': 'Faka ku-Kalishi', 'cart_empty': 'Ikalishi lakho likhululekile.', 'cart_empty_sub': 'Buka imakethe kute ufake imikhicito.',
        'continue_shopping': 'Chubeka Utsenga', 'proceed_checkout': 'Chubeka ku-Checkout',
        'checkout_title': 'Checkout', 'order_summary': 'Sifinyeto se-oda', 'total': 'Konkhe', 'payment_method': 'Khetsa Indlela yekukhokha',
        'confirm_order': 'Cinisekisa I-oda', 'order_success': 'I-oda ifakwe ngekuphumelela!', 'order_id': 'Inombolo ye-oda', 'pin': 'I-PIN yekugcina',
        'dashboard_btn': 'Iya ku-Dashboard'
    }
}

# --- MARKETPLACE & CART LOGIC ---
@login_required
def marketplace_view(request):
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    products = ProduceListing.objects.filter(status='Available', available_quantity_kg__gt=0)
    return render(request, 'marketplace.html', {'t': translations, 'products': products, 'current_lang': lang})

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        quantity = float(request.POST.get('quantity', 1))
        
        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity
            
        request.session['cart'] = cart
        messages.success(request, "Item added to cart successfully.")
    return redirect('marketplace')

@login_required
def cart_view(request):
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    cart = request.session.get('cart', {})
    
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = get_object_or_404(ProduceListing, id=pid)
        subtotal = product.price_per_kg * Decimal(qty)
        total += subtotal
        cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})

    return render(request, 'cart.html', {'t': translations, 'cart_items': cart_items, 'total': total, 'current_lang': lang})

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart')

# --- CHECKOUT & ORDER PROCESSING ---


@login_required
@role_required(['BUYER'])
def checkout_view(request):
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('marketplace')

    drivers = User.objects.filter(role='DRIVER', is_available=True, is_verified=True)
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = get_object_or_404(ProduceListing, id=pid)
        subtotal = product.price_per_kg * Decimal(qty)
        total += subtotal
        cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})

    if request.method == 'POST':
        driver_id = request.POST.get('driver_id')
        payment_method = request.POST.get('payment_method')
        selected_driver = User.objects.get(id=driver_id) if driver_id else None
        transport_fee = Decimal('150.00')

        # Get Dynamic Commission
        setting = PlatformSetting.objects.first()
        commission_rate = setting.commission_rate if setting else Decimal('10.00')

        with transaction.atomic():
            # 1. Create the Order (Status: Pending Payment)
            order = Order.objects.create(
                buyer=request.user, matched_driver=selected_driver,
                total_produce_amount=total, transport_fee=transport_fee,
                payment_method=payment_method,
                status='Pending' # Will become IN_ESCROW once payment succeeds
            )
            
            # 2. Create Order Items and Split by Farmer
                        # 2. Create Order Items and Split by Farmer
            farmer_totals = {}
            for item in cart_items:
                # FIX: Convert the float quantity from the session cart to a Decimal
                qty_decimal = Decimal(str(item['quantity']))
                
                OrderItem.objects.create(
                    order=order, produce=item['product'],
                    quantity_ordered_kg=qty_decimal, 
                    subtotal=item['subtotal']
                )
                # Deduct inventory using the safe Decimal variable
                item['product'].available_quantity_kg -= qty_decimal
                if item['product'].available_quantity_kg <= 0:
                    item['product'].status = 'Sold Out'
                item['product'].save()

                # Group totals by farmer (using the Decimal variable)
                farmer_id = item['product'].farmer.id
                if farmer_id not in farmer_totals:
                    farmer_totals[farmer_id] = Decimal('0.00')
                farmer_totals[farmer_id] += item['subtotal']

                # Group totals by farmer
                farmer_id = item['product'].farmer.id
                if farmer_id not in farmer_totals:
                    farmer_totals[farmer_id] = Decimal('0.00')
                farmer_totals[farmer_id] += item['subtotal']

            # 3. Create Order Fulfilments for each farmer
            for farmer_id, gross in farmer_totals.items():
                farmer = User.objects.get(id=farmer_id)
                comm_amt = (gross * commission_rate) / Decimal('100.00')
                net_amt = gross - comm_amt
                
                OrderFulfilment.objects.create(
                    order=order, farmer=farmer, status='PENDING',
                    gross_amount=gross, commission_amount=comm_amt, net_amount=net_amt
                )

            # 4. Create Payment Transaction
            payment_ref = f"SL-{get_random_string(8).upper()}"
            PaymentTransaction.objects.create(
                order=order, method=payment_method,
                reference=payment_ref, amount=order.total_amount
            )
            
            # 5. Clear cart and send PIN SMS
            request.session['cart'] = {}
            email_message = f"Your order #{order.id} is placed. PIN: {order.verification_pin}. Await payment confirmation."
            print(f"\n--- SIMULATED SMS ---\nTo: {request.user.phone_number}\n{email_message}\n---------------------\n")

            # Redirect to the Payment Gateway Page
            return redirect('process_payment', order_id=order.id)

    return render(request, 'checkout.html', {
        't': translations, 'cart_items': cart_items, 'total': total, 
        'drivers': drivers, 'current_lang': lang
    })

# core/views.py

@login_required
@role_required(['FARMER'])
def farmer_fulfilments(request):
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    request.session['lang'] = lang
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    
    fulfilments = OrderFulfilment.objects.filter(farmer=request.user).order_by('-order__created_at')
    
    return render(request, 'farmer_fulfilments.html', {
        't': translations, 
        'current_lang': lang,
        'fulfilments': fulfilments
    })


@login_required
@role_required(['FARMER'])
def complete_fulfilment(request, fulfilment_id):
    if request.method == 'POST':
        fulfilment = get_object_or_404(OrderFulfilment, id=fulfilment_id, farmer=request.user)
        if fulfilment.status == 'CONFIRMED':
            fulfilment.status = 'COMPLETED'
            fulfilment.completed_at = timezone.now()
            fulfilment.save()
            messages.success(request, "Your produce has been marked as dispatched/completed.")
        return redirect('farmer_fulfilments')

@login_required
@role_required(['BUYER'])
def archive_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, buyer=request.user)
        if order.status in ['Completed', 'Cancelled']:
            order.is_archived_by_buyer = True
            order.save()
            messages.success(request, "Order archived.")
    return redirect('dashboard')

# core/views.py

@login_required
def admin_reports(request):
    if not request.user.is_superuser: return redirect('dashboard')
    
    # Analytics
    fulfilments = OrderFulfilment.objects.filter(status='COMPLETED')
    total_revenue = fulfilments.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0.00
    
    context = {
        'fulfilments': fulfilments,
        'total_revenue': total_revenue,
    }
    return render(request, 'admin_reports.html', context)

@login_required
def export_csv(request):
    if not request.user.is_superuser: return redirect('dashboard')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sivunolink_financials.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Date', 'Farmer', 'Gross Amount', 'Commission', 'Net Payout'])
    
    fulfilments = OrderFulfilment.objects.filter(status='COMPLETED')
    for f in fulfilments:
        writer.writerow([f.order.id, f.completed_at.strftime("%Y-%m-%d"), f.farmer.username, f.gross_amount, f.commission_amount, f.net_amount])
        
    return response

@login_required
def admin_settings(request):
    if not request.user.is_superuser: return redirect('dashboard')
    setting, created = PlatformSetting.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        new_rate = request.POST.get('commission_rate')
        setting.commission_rate = new_rate
        setting.save()
        messages.success(request, f"Commission updated to {new_rate}%")
        return redirect('admin_settings')
        
    return render(request, 'admin_commission.html', {'setting': setting})

# NEW: Payment Gateway Simulation View
@login_required
@role_required(['BUYER'])
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    payment = order.payments.last()

    if request.method == 'POST':
        # Simulate Gateway processing
        action = request.POST.get('action')
        
        with transaction.atomic():
            if action == 'success':
                payment.status = 'SUCCESS'
                payment.save()
                
                # Lock funds in Escrow
                order.status = 'IN_ESCROW'
                order.save()
                
                EscrowTransaction.objects.create(order=order, amount_held=order.total_amount, status='HELD')
                
                # Confirm Farmer Fulfilments
                for f in order.fulfilments.all():
                    f.status = 'CONFIRMED'
                    f.save()
                    
                messages.success(request, f"Payment Successful! Order #{order.id} is now in Escrow.")
                return redirect('dashboard')
            else:
                payment.status = 'FAILED'
                payment.save()
                messages.error(request, "Payment failed or cancelled.")
                return redirect('dashboard')

    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    return render(request, 'payment_gateway.html', {'order': order, 'payment': payment, 't': translations, 'current_lang': lang})

# --- DRIVER DELIVERY VERIFICATION ---
@login_required
@role_required(['DRIVER', 'ADMIN'])
def verify_delivery_pin_view(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        submitted_pin = request.POST.get('pin')
        
        try:
            with transaction.atomic():
                # 1. Find the order by ID and PIN
                order = Order.objects.select_for_update().get(id=order_id, verification_pin=submitted_pin)
                escrow = order.escrow

                # 2. SECURITY CHECK: Ensure the logged-in driver is the assigned driver
                # (Admins are allowed to override for dispute resolution)
                if not request.user.is_superuser and order.matched_driver != request.user:
                    messages.error(request, "Security Alert: You are not the assigned driver for this order.")
                    return redirect('dashboard')

                # 3. Proceed with release if authorized
                if escrow.status == 'HELD':
                    order.status = 'Completed'
                    order.save()
                    
                    escrow.status = 'RELEASED'
                    escrow.save()

                    platform_commission = order.total_produce_amount * Decimal('0.10') 
                    
                    AuditLog.objects.create(actor=request.user, action=f"Released Escrow. Commission: E{platform_commission:.2f}", target_entity=f"Order #{order.id}")
                    messages.success(request, f"Success! Order #{order.id} completed. Funds released to farmer.")
                else:
                    messages.warning(request, "This order has already been completed.")
                    
        except Order.DoesNotExist:
            messages.error(request, "Invalid Order ID or PIN. Please check and try again.")
        except Exception as e:
            messages.error(request, f"Transaction failed: {str(e)}")

    return redirect('dashboard')

# --- EXISTING BASIC VIEWS ---
def register_buyer(request):
    if request.method == 'POST':
        form = BuyerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = BuyerSignUpForm()
    return render(request, 'registration/register.html', {'form': form})

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    request.session['lang'] = lang
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    
    # Fetch the 3 most recently listed available produce items
    featured_produce = ProduceListing.objects.filter(status='Available').order_by('-created_at')[:3]
    
    return render(request, 'landing.html', {
        't': translations, 
        'current_lang': lang,
        'featured_produce': featured_produce
    })

def contact_us(request):
    return render(request, 'contact.html')
    
    # NEW: Fetch the 3 most recently listed produce items
    featured_produce = ProduceListing.objects.filter(status='Available').order_by('-created_at')[:3]
    
    return render(request, 'landing.html', {
        't': translations, 
        'current_lang': lang,
        'featured_produce': featured_produce # Pass to template
    })

# Update your LANG_DICT by adding these keys:
# 'en': { ..., 'my_orders': 'My Recent Orders', 'no_orders': 'You have not placed any orders yet.', 'view_marketplace': 'Visit Marketplace', 'order_status': 'Status', 'driver': 'Driver', 'total_amount': 'Total Amount' }
# 'sz': { ..., 'my_orders': 'Ema-oda Ami', 'no_orders': 'Awukafaki ma-oda nyalo.', 'view_marketplace': 'Buka Imakethe', 'order_status': 'Simo', 'driver': 'Umshayeli', 'total_amount': 'Imali Iyonkhe' }


def dashboard(request):
    if not request.user.is_authenticated: return redirect('landing_page')
    if request.user.is_superuser: return redirect('custom_admin_settings')

    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    request.session['lang'] = lang
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    context = {'t': translations, 'current_lang': lang}

    if request.user.role == 'DRIVER':
        active_orders = Order.objects.filter(
            matched_driver=request.user, 
            status__in=['Assigned', 'In Transit']
        ).order_by('-created_at')
        context['driver_orders'] = active_orders
        return render(request, 'driver_dashboard.html', context)
        
    elif request.user.role == 'BUYER':
        # ONLY fetch Active Orders for the main dashboard
        active_orders = Order.objects.filter(
            buyer=request.user,
            status__in=['Pending', 'IN_ESCROW', 'Assigned', 'In Transit', 'DISPUTED']
        ).order_by('-created_at')
        context['buyer_orders'] = active_orders
        return render(request, 'dashboard.html', context)

    elif request.user.role == 'FARMER':
        return redirect('farmer_fulfilments')

    return redirect('landing_page')

# NEW: Buyer Order History View
@login_required
def buyer_history(request):
    if request.user.role != 'BUYER': return redirect('dashboard')
    
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    
    # Fetch ONLY Completed or Cancelled orders
    history_orders = Order.objects.filter(
        buyer=request.user, 
        status__in=['Completed', 'Cancelled']
    ).order_by('-created_at')
    
    return render(request, 'buyer_history.html', {'t': translations, 'history_orders': history_orders, 'current_lang': lang})

# NEW: Delete Order View
@login_required
def delete_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, buyer=request.user)
        # Security check: Can only delete if Completed or Cancelled
        if order.status in ['Completed', 'Cancelled']:
            order.delete()
            messages.success(request, "Order permanently deleted from your history.")
        else:
            messages.error(request, "You cannot delete an active order.")
    return redirect('buyer_history')

# --- DRIVER PORTAL LOGIC ---
@login_required
@role_required(['DRIVER'])
def driver_portal(request):
    my_deliveries = Order.objects.filter(matched_driver=request.user).exclude(status='Completed').order_by('-created_at')
    
    if request.method == 'POST' and 'toggle_availability' in request.POST:
        request.user.is_available = not request.user.is_available
        request.user.save()
        messages.success(request, f"Status updated.")
        return redirect('driver_portal')

    return render(request, 'driver_portal.html', {'deliveries': my_deliveries})

# --- CUSTOM 2FA LOGIN FLOW ---
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    def form_valid(self, form):
        user = form.get_user()
        OTPRecord.objects.create(user=user, otp_code=str(random.randint(100000, 999999)))
        self.request.session['pre_2fa_user_id'] = user.id
        return redirect('verify_otp')

@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser: return redirect('dashboard')
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        if target_user != request.user:
            target_user.delete()
            messages.success(request, "User permanently deleted.")
    return redirect('admin_users')

def verify_otp_view(request):
    user_id = request.session.get('pre_2fa_user_id')
    
    if not user_id:
        return redirect('login')
        
    if request.method == 'POST':
        submitted_otp = request.POST.get('otp')
        otp_record = OTPRecord.objects.filter(user_id=user_id, is_used=False).order_by('-created_at').first()
        
        if otp_record and otp_record.otp_code == submitted_otp:
            otp_record.is_used = True
            otp_record.save()
            
            # SAFE USER LOGIN (Prevents 500 error if user was deleted)
            try:
                user = User.objects.get(id=user_id)
                login(request, user)
                request.session.pop('pre_2fa_user_id', None)
                return redirect('dashboard')
            except User.DoesNotExist:
                messages.error(request, "User session expired. Please log in again.")
                return redirect('login')
        else:
            messages.error(request, "Invalid or expired OTP. Please try again.")
            
    latest_otp = OTPRecord.objects.filter(user_id=user_id, is_used=False).order_by('-created_at').first()
    simulated_code = latest_otp.otp_code if latest_otp else None
    
    return render(request, 'registration/verify_otp.html', {'simulated_code': simulated_code})

# --- ADMIN HUB & SUBPAGES ---
@login_required
def custom_admin_settings(request):
    if not request.user.is_superuser: return redirect('dashboard')
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    return render(request, 'admin_hub.html', {'t': translations, 'current_lang': lang})

@login_required
def admin_users(request):
    if not request.user.is_superuser: return redirect('dashboard')
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    users = User.objects.all().order_by('-date_joined')
    logs = AuditLog.objects.all().order_by('-timestamp')[:10]
    return render(request, 'admin_users.html', {'t': translations, 'users': users, 'logs': logs})

@login_required
def admin_approvals(request):
    if not request.user.is_superuser: return redirect('dashboard')
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    
    pending_users = User.objects.filter(is_verified=False).order_by('-date_joined')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        target_user = get_object_or_404(User, id=user_id)
        target_user.is_verified = True
        target_user.save()
        AuditLog.objects.create(actor=request.user, action="Approved User", target_entity=target_user.username)
        messages.success(request, f"User {target_user.username} approved successfully.")
        return redirect('admin_approvals')

    return render(request, 'admin_approvals.html', {'t': translations, 'pending_users': pending_users})

@login_required
def admin_driver_assignment(request):
    if not request.user.is_superuser: return redirect('dashboard')
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    
    # FIX: Look for orders that are IN_ESCROW or Pending and have no driver yet
    pending_orders = Order.objects.filter(status__in=['Pending', 'IN_ESCROW'], matched_driver__isnull=True)
    drivers = User.objects.filter(role='DRIVER', is_available=True, is_verified=True)
    
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        driver_id = request.POST.get('driver_id')
        order = get_object_or_404(Order, id=order_id)
        driver = get_object_or_404(User, id=driver_id)
        
        order.matched_driver = driver
        order.status = 'Assigned' # Move status to Assigned
        order.save()
        
        AuditLog.objects.create(actor=request.user, action="Assigned Driver", target_entity=f"Driver {driver.username} to Order #{order.id}")
        messages.success(request, f"Driver {driver.username} assigned to Order #{order.id}.")
        return redirect('admin_driver_assignment')

    return render(request, 'admin_assign.html', {'t': translations, 'pending_orders': pending_orders, 'drivers': drivers})

@login_required
def admin_monitoring(request):
    if not request.user.is_superuser: return redirect('dashboard')
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    active_orders = Order.objects.filter(status__in=['Assigned', 'In Transit']).order_by('-created_at')
    return render(request, 'admin_monitor.html', {'t': translations, 'active_orders': active_orders})

@login_required
def admin_reports(request):
    if not request.user.is_superuser: 
        return redirect('dashboard')
    
    lang = request.GET.get('lang', request.session.get('lang', 'en'))
    request.session['lang'] = lang
    translations = LANG_DICT.get(lang, LANG_DICT['en'])
    
    # 1. Calculate Financials
    fulfilments = OrderFulfilment.objects.filter(status='COMPLETED')
    total_revenue = fulfilments.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0.00
    completed_orders = fulfilments.count()
    
    # 2. Calculate Top Selling Produce
    top_produce = OrderItem.objects.filter(
        order__fulfilments__status='COMPLETED'
    ).values(
        'produce__product_name'
    ).annotate(
        total_kg_sold=Sum('quantity_ordered_kg')
    ).order_by('-total_kg_sold')[:5]
    
    context = {
        't': translations,
        'current_lang': lang,
        'total_revenue': total_revenue,
        'completed_orders': completed_orders,
        'top_produce': top_produce
    }
    return render(request, 'admin_reports.html', context)

@login_required
def toggle_user_status(request, user_id):
    if not request.user.is_superuser: return redirect('dashboard')
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        if target_user != request.user:
            target_user.is_active = not target_user.is_active
            target_user.save()
            action = "Activated User" if target_user.is_active else "Suspended User"
            AuditLog.objects.create(actor=request.user, action=action, target_entity=target_user.username)
            messages.success(request, f"User {target_user.username} status changed.")
    return redirect('admin_users')

# 1. UPDATED BUYER VIEW (Captures the reason)
@login_required
def raise_dispute(request, order_id):
    if request.method == 'POST':
        reason = request.POST.get('dispute_reason', 'No reason provided.')
        order = get_object_or_404(Order, id=order_id, buyer=request.user)
        
        order.status = 'DISPUTED'
        order.save()
        
        if hasattr(order, 'escrow'):
            escrow = order.escrow
            escrow.status = 'DISPUTED'
            escrow.dispute_reason = reason
            escrow.save()
            
        AuditLog.objects.create(actor=request.user, action="Raised Dispute", target_entity=f"Order #{order.id}")
        messages.error(request, "Dispute raised. Funds are now frozen in Escrow pending Admin review.")
        
    return redirect('dashboard')

# 2. NEW ADMIN VIEW (List all disputes)
@login_required
def admin_disputes(request):
    if not request.user.is_superuser: return redirect('dashboard')
    
    # Get all escrow transactions that are currently in dispute
    disputed_escrows = EscrowTransaction.objects.filter(status='DISPUTED').order_by('-date_updated')
    
    return render(request, 'admin_disputes.html', {'escrows': disputed_escrows})

# 3. NEW ADMIN VIEW (Resolve a specific dispute)
@login_required
def resolve_dispute(request, escrow_id):
    if not request.user.is_superuser: return redirect('dashboard')
    
    if request.method == 'POST':
        escrow = get_object_or_404(EscrowTransaction, id=escrow_id)
        resolution_note = request.POST.get('resolution_note', 'Resolved by Admin.')
        action = request.POST.get('action')
        
        # Save the Admin's note
        escrow.admin_resolution_notes = resolution_note
        
        if action == 'release':
            escrow.status = 'RELEASED'
            escrow.order.status = 'Completed'
            messages.success(request, f"Funds released to Farmer for Order #{escrow.order.id}.")
        elif action == 'refund':
            escrow.status = 'REFUNDED'
            escrow.order.status = 'Cancelled'
            messages.success(request, f"Funds refunded to Buyer for Order #{escrow.order.id}.")
            
        escrow.save()
        escrow.order.save()
        
        AuditLog.objects.create(actor=request.user, action=f"Resolved Dispute ({action.upper()})", target_entity=f"Order #{escrow.order.id}")
        
    return redirect('admin_disputes')