from io import BytesIO
import base64

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Case, When, Value, IntegerField, Q, Sum, Count
from django.contrib import messages
from django.utils import timezone

from .models import (
    Category, Package, Booking, Payment, Wishlist,
    Review, Coupon, ContactEnquiry, BlogPost
)

UPI_ID = 'nihal8129587568-1@okaxis'
PAYEE_NAME = 'Muhammed Nihal'


def make_dynamic_upi_qr(amount):
    try:
        import qrcode
        upi_url = f'upi://pay?pa={UPI_ID}&pn={PAYEE_NAME.replace(" ", "%20")}&am={amount}&cu=INR&tn=TravelWorld%20Booking'
        img = qrcode.make(upi_url)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()
    except Exception:
        return ''


def make_ticket_qr(booking):
    try:
        import qrcode
        ticket_data = (
            f"TravelWorld E-Ticket\n"
            f"Booking ID: TW-{booking.id}\n"
            f"Name: {booking.full_name}\n"
            f"Package: {booking.package.name}\n"
            f"Travel Date: {booking.travel_date}\n"
            f"Amount: ₹{booking.total_amount}\n"
            f"Status: {booking.status}"
        )
        img = qrcode.make(ticket_data)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    except Exception:
        return ""


def seed_data():
    categories = [
        ('Honeymoon','honeymoon','💑','Romantic couple trips, candle light dinner and premium stays'),
        ('Nature','nature','🌿','Hill stations, waterfalls, forests and peaceful escapes'),
        ('Adventure','adventure','🏕️','Trekking, snow, camping and thrilling activities'),
        ('Beach','beach','🏖️','Beaches, islands, water sports and sunset stays'),
        ('Family','family','👨‍👩‍👧','Safe, comfortable family vacation packages'),
        ('Pilgrimage','pilgrimage','🛕','Spiritual trips and temple tours'),
        ('Luxury','luxury','⭐','Premium hotels, villas and international holidays'),
        ('Wildlife','wildlife','🐘','Forest resorts, safaris and wildlife experiences'),
    ]

    for name, slug, icon, desc in categories:
        Category.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'icon': icon, 'description': desc}
        )

    def cat(slug):
        return Category.objects.get(slug=slug)

    packages = [
        ('Goa','India','Goa','beach','beach,nature,family,party,water sports',20000,4,3,'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1200','Beaches, churches, nightlife, seafood and water sports.','Day 1: Arrival and beach walk\nDay 2: North Goa sightseeing\nDay 3: Water sports and sunset cruise\nDay 4: Shopping and departure',True),
        ('Munnar','India','Kerala','nature','nature,honeymoon,hillstation,tea garden',18000,3,2,'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=1200','Tea gardens, misty hills and peaceful resorts in Kerala.','Day 1: Tea gardens\nDay 2: Mattupetty Dam and Echo Point\nDay 3: Departure',True),
        ('Maldives','Maldives','Male','honeymoon','honeymoon,beach,luxury,nature,island',70000,5,4,'https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=1200','Water villas, beaches and premium honeymoon experience.','Day 1: Resort check-in\nDay 2: Snorkeling\nDay 3: Island hopping\nDay 4: Spa and dinner\nDay 5: Departure',True),
        ('Dubai','UAE','Dubai','luxury','luxury,family,shopping,desert,city',50000,5,4,'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1200','Burj Khalifa, desert safari, Dubai Mall and Marina tour.','Day 1: City tour\nDay 2: Burj Khalifa\nDay 3: Desert safari\nDay 4: Shopping\nDay 5: Departure',True),
        ('Paris','France','Paris','honeymoon','honeymoon,luxury,culture,romantic',90000,6,5,'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1200','Eiffel Tower, Louvre, Seine River and romantic city experiences.','Day 1: Arrival\nDay 2: Eiffel Tower\nDay 3: Louvre\nDay 4: Seine cruise\nDay 5: Shopping\nDay 6: Departure',True),
        ('Manali','India','Himachal Pradesh','adventure','adventure,nature,honeymoon,snow,trekking',25000,5,4,'https://images.unsplash.com/photo-1593181629936-11c609b8db9b?w=1200','Snow mountains, adventure activities and scenic valleys.','Day 1: Arrival\nDay 2: Solang Valley\nDay 3: Local sightseeing\nDay 4: Adventure activities\nDay 5: Departure',False),
        ('Kashmir','India','Srinagar','nature','nature,honeymoon,family,snow,houseboat',35000,5,4,'https://www.namasteindiatrip.com/blog/wp-content/uploads/2014/06/Wintry-White-Experience-in-Kashmir.jpg','Houseboats, gardens, valleys and snow mountain views.','Day 1: Srinagar\nDay 2: Gulmarg\nDay 3: Pahalgam\nDay 4: Houseboat\nDay 5: Departure',True),
        ('Bali','Indonesia','Bali','beach','honeymoon,beach,nature,luxury,temple',65000,6,5,'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1200','Beaches, temples, waterfalls and romantic resorts.','Day 1: Arrival\nDay 2: Ubud\nDay 3: Beaches\nDay 4: Temple tour\nDay 5: Shopping\nDay 6: Departure',False),
        ('Tokyo','Japan','Tokyo','family','family,culture,city,shopping,anime',95000,6,5,'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1200','Modern city, temples, anime culture, shopping and food.','Day 1: Arrival\nDay 2: Tokyo Tower\nDay 3: Shibuya\nDay 4: Disneyland\nDay 5: Shopping\nDay 6: Departure',False),
        ('Switzerland','Europe','Interlaken','nature','nature,luxury,honeymoon,snow,mountains',120000,7,6,'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200','Swiss Alps, lakes, trains and luxury mountain views.','Day 1: Zurich\nDay 2: Lucerne\nDay 3: Interlaken\nDay 4: Jungfraujoch\nDay 5: Lake tour\nDay 6: Shopping\nDay 7: Departure',True),
        ('Ooty','India','Tamil Nadu','nature','nature,family,hillstation,lake',16000,3,2,'https://www.oyorooms.com/travel-guide/wp-content/uploads/2019/10/Munnar.jpg','Cool climate, botanical garden, lake and mountain train.','Day 1: Arrival\nDay 2: Sightseeing\nDay 3: Departure',False),
        ('Rajasthan','India','Jaipur','family','family,culture,desert,heritage,palace',28000,5,4,'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=1200','Palaces, desert, forts and royal culture.','Day 1: Jaipur\nDay 2: Forts\nDay 3: Jodhpur\nDay 4: Desert camp\nDay 5: Departure',False),
        ('Alleppey Houseboat','India','Kerala','honeymoon','honeymoon,nature,backwater,houseboat,family',22000,2,1,'https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=1200','Private houseboat stay through calm Kerala backwaters.','Day 1: Houseboat check-in and cruise\nDay 2: Village visit and departure',True),
        ('Wayanad','India','Kerala','nature','nature,adventure,waterfalls,caves,wildlife',17000,3,2,'https://images.unsplash.com/photo-1548013146-72479768bada?w=1200','Waterfalls, caves, forest resorts and green hills.','Day 1: Resort check-in\nDay 2: Edakkal Caves and waterfalls\nDay 3: Departure',False),
        ('Lakshadweep','India','Kavaratti','beach','beach,island,nature,water sports',45000,5,4,'https://images.unsplash.com/photo-1500375592092-40eb2168fd21?w=1200','Clean islands, coral beaches and peaceful blue waters.','Day 1: Arrival\nDay 2: Beach leisure\nDay 3: Water sports\nDay 4: Island tour\nDay 5: Departure',True),
        ('Andaman','India','Port Blair','beach','beach,island,history,honeymoon,scuba',42000,5,4,'https://images.unsplash.com/photo-1586500036706-41963de24d8b?w=1200','Cellular Jail, Havelock Island, scuba diving and beaches.','Day 1: Port Blair\nDay 2: Havelock\nDay 3: Scuba\nDay 4: Cellular Jail\nDay 5: Departure',False),
        ('Rishikesh','India','Uttarakhand','adventure','adventure,rafting,yoga,nature,camping',19000,3,2,'https://images.unsplash.com/photo-1597074866923-dc0589150358?w=1200','River rafting, camping, yoga and Ganga views.','Day 1: Arrival and camp\nDay 2: Rafting\nDay 3: Yoga and departure',False),
        ('Varanasi','India','Uttar Pradesh','pilgrimage','pilgrimage,spiritual,temple,river,culture',14000,3,2,'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=1200','Ganga Aarti, temples, boat ride and spiritual experience.','Day 1: Arrival\nDay 2: Temple tour and Ganga Aarti\nDay 3: Departure',False),
        ('Thailand','Thailand','Phuket','beach','beach,family,shopping,honeymoon,island',55000,5,4,'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=1200','Phuket beaches, island tours, shopping and nightlife.','Day 1: Arrival\nDay 2: Phi Phi Island\nDay 3: City tour\nDay 4: Shopping\nDay 5: Departure',False),
        ('Singapore','Singapore','Singapore','family','family,luxury,city,shopping,universal studios',60000,4,3,'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=1200','Universal Studios, Marina Bay, Sentosa and city tour.','Day 1: Arrival\nDay 2: Universal Studios\nDay 3: City tour\nDay 4: Departure',True),
        ('Malaysia','Malaysia','Kuala Lumpur','family','family,city,nature,shopping',48000,5,4,'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1200','Kuala Lumpur, Genting Highlands and shopping tour.','Day 1: Arrival\nDay 2: KL city\nDay 3: Genting\nDay 4: Shopping\nDay 5: Departure',False),
        ('Meghalaya','India','Shillong','nature','nature,waterfalls,caves,adventure',30000,5,4,'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1200','Living root bridges, waterfalls, caves and clean villages.','Day 1: Shillong\nDay 2: Cherrapunji\nDay 3: Dawki\nDay 4: Mawlynnong\nDay 5: Departure',False),
        ('Coorg','India','Karnataka','nature','nature,honeymoon,coffee,hillstation',19000,3,2,'https://images.unsplash.com/photo-1548013146-72479768bada?w=1200','Coffee estates, waterfalls, resorts and cool climate.','Day 1: Arrival\nDay 2: Abbey Falls and estate visit\nDay 3: Departure',False),
        ('Sikkim','India','Gangtok','nature','nature,snow,monastery,family',38000,5,4,'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200','Gangtok, Tsomgo Lake, monasteries and mountain views.','Day 1: Arrival\nDay 2: Gangtok\nDay 3: Tsomgo Lake\nDay 4: Monastery tour\nDay 5: Departure',False),
        ('Jim Corbett','India','Uttarakhand','wildlife','wildlife,nature,safari,family',21000,3,2,'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=1200','Wildlife safari, forest stay and nature photography.','Day 1: Forest resort\nDay 2: Jeep safari\nDay 3: Departure',False),
    ]

    for name, country, city, category, tags, price, days, nights, img, desc, itinerary, featured in packages:
        Package.objects.get_or_create(
            name=name,
            defaults={
                'country': country,
                'city': city,
                'category': cat(category),
                'tags': tags,
                'price': price,
                'old_price': int(price * 1.18),
                'days': days,
                'nights': nights,
                'image': img,
                'description': desc,
                'itinerary': itinerary,
                'is_featured': featured,
                'seats': 60,
                'hotel': 'Premium selected hotel',
                'flight': 'Flight assistance available',
                'map_query': f'{name} {city} {country}',
            }
        )

    Coupon.objects.get_or_create(code='NEWUSER10', defaults={'discount_percent': 10, 'min_amount': 20000})
    Coupon.objects.get_or_create(code='TRAVEL20', defaults={'discount_percent': 20, 'min_amount': 50000})
    Coupon.objects.get_or_create(code='HONEYMOON15', defaults={'discount_percent': 15, 'min_amount': 40000})

    BlogPost.objects.get_or_create(
        slug="best-honeymoon-destinations",
        defaults={
            "title": "Best Honeymoon Destinations for Couples",
            "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200",
            "category": "Honeymoon",
            "short_description": "Explore romantic destinations like Maldives, Bali, Kashmir and Paris.",
            "content": "Honeymoon trips are special because they create lifetime memories. Popular destinations include Maldives, Bali, Kashmir, Paris and Switzerland. Couples can choose beach resorts, mountain stays, luxury villas and peaceful nature destinations.",
            "is_published": True,
        }
    )

 
    BlogPost.objects.get_or_create(
        slug="why-book-travel-packages",
        defaults={
            "title": "Why Travel Packages Are Better",
            "image": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1200",
            "category": "Guide",
            "short_description": "Understand why complete packages save time and money.",
            "content": "Travel packages help users book hotel, transport, sightseeing and assistance together. They reduce confusion, save time and give a better planned experience.",
            "is_published": True,
        }
    )


def package_query(queryset, query):
    if not query:
        return queryset.order_by('-is_featured', 'price')

    return queryset.filter(
        Q(name__icontains=query) |
        Q(country__icontains=query) |
        Q(city__icontains=query) |
        Q(tags__icontains=query) |
        Q(category__name__icontains=query) |
        Q(description__icontains=query)
    ).annotate(
        priority=Case(
            When(name__iexact=query, then=Value(0)),
            When(name__istartswith=query, then=Value(1)),
            When(city__iexact=query, then=Value(2)),
            When(city__istartswith=query, then=Value(3)),
            When(country__istartswith=query, then=Value(4)),
            When(category__name__iexact=query, then=Value(5)),
            When(tags__icontains=query, then=Value(6)),
            default=Value(7),
            output_field=IntegerField()
        )
    ).order_by('priority', 'price', '-rating')


def home(request):
    # seed_data()

    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    max_budget = request.GET.get('budget', '').strip()

    packages = Package.objects.filter(is_active=True).select_related('category')

    if category:
        packages = packages.filter(category__slug=category)

    if max_budget.isdigit():
        packages = packages.filter(price__lte=int(max_budget))

    packages = package_query(packages, query)
    all_packages = Package.objects.filter(is_active=True).select_related('category')

    return render(request, 'travelapp/home.html', {
        'packages': packages,
        'all_packages': all_packages,
        'categories': Category.objects.all(),
        'query': query,
        'selected_category': category,
        'budget': max_budget,
        'featured': Package.objects.filter(is_featured=True)[:6],
    })


def category_packages(request, slug):
    seed_data()
    cat_obj = get_object_or_404(Category, slug=slug)
    packages = Package.objects.filter(category=cat_obj, is_active=True).order_by('price')

    return render(request, 'travelapp/category.html', {
        'cat': cat_obj,
        'packages': packages,
        'categories': Category.objects.all()
    })


def package_details(request, id):
    package = get_object_or_404(Package, id=id, is_active=True)
    reviews = package.reviews.select_related('user').order_by('-created_at')
    related = Package.objects.filter(category=package.category, is_active=True).exclude(id=id)[:4]

    return render(request, 'travelapp/package_details.html', {
        'package': package,
        'reviews': reviews,
        'related': related,
        'categories': Category.objects.all()
    })


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('home')

    return render(request, 'travelapp/register.html')

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)

            if user.is_staff:
                return redirect('dashboard')

            return redirect('home')

        messages.error(request, 'Invalid username or password')

    return render(request, 'travelapp/login.html')


def admin_login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            if user.is_staff:
                login(request, user)
                return redirect('dashboard')

            messages.error(request, 'This login is only for admin.')
            return redirect('admin_login')

        messages.error(request, 'Invalid admin username or password')

    return render(request, 'travelapp/admin_login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


@login_required
def booking(request, package_id):
    package = get_object_or_404(Package, id=package_id, is_active=True)

    if request.method == 'POST':
        members = int(request.POST.get('members', 1))

        if members > package.available_seats:
            messages.error(request, 'Selected members exceed available seats.')
            return redirect('booking', package_id=package.id)

        base = package.price * members
        code = request.POST.get('coupon_code', '').upper().strip()
        discount = 0

        if code:
            coupon = Coupon.objects.filter(code=code, active=True, min_amount__lte=base).first()
            if coupon:
                discount = base * coupon.discount_percent // 100
            else:
                messages.warning(request, 'Coupon not applied. Minimum amount or coupon code is invalid.')

        booking_obj = Booking.objects.create(
            user=request.user,
            package=package,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            travel_date=request.POST.get('travel_date'),
            members=members,
            coupon_code=code,
            discount_amount=discount,
            total_amount=base - discount
        )

        request.session['booking_id'] = booking_obj.id
        return redirect('payment')

    return render(request, 'travelapp/booking.html', {'package': package})
@login_required
@login_required
@login_required
def payment(request):
    import urllib.parse

    booking_obj = get_object_or_404(
        Booking,
        id=request.session.get('booking_id'),
        user=request.user
    )

    payment_obj, _ = Payment.objects.get_or_create(
        booking=booking_obj,
        defaults={
            'amount': booking_obj.total_amount,
            'upi_id': UPI_ID
        }
    )

    dynamic_qr = make_dynamic_upi_qr(booking_obj.total_amount)

    if request.method == 'POST':
        payment_obj.transaction_id = request.POST.get(
            'transaction_id',
            'DEMO-UPI-PAID'
        )
        payment_obj.amount = booking_obj.total_amount
        payment_obj.upi_id = UPI_ID
        payment_obj.payment_status = 'Success'
        payment_obj.paid_on = timezone.now()
        payment_obj.save()

        booking_obj.status = 'Confirmed'
        booking_obj.save()

        phone = booking_obj.phone.replace("+", "").replace(" ", "").replace("-", "")

        if len(phone) == 10:
            phone = "91" + phone

        message = f"""Hello {booking_obj.full_name},

Your TravelWorld booking is confirmed.

Booking ID: TW-{booking_obj.id}
Package: {booking_obj.package.name}
Destination: {booking_obj.package.city}, {booking_obj.package.country}
Travel Date: {booking_obj.travel_date}
Travellers: {booking_obj.members}
Amount Paid: ₹{booking_obj.total_amount}

Thank you for choosing TravelWorld."""

        whatsapp_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/{phone}?text={whatsapp_message}"

        return render(
            request,
            'travelapp/payment.html',
            {
                'booking': booking_obj,
                'payment': payment_obj,
                'dynamic_qr': dynamic_qr,
                'upi_id': UPI_ID,
                'payment_success': True,
                'whatsapp_url': whatsapp_url,
            }
        )

    return render(
        request,
        'travelapp/payment.html',
        {
            'booking': booking_obj,
            'payment': payment_obj,
            'dynamic_qr': dynamic_qr,
            'upi_id': UPI_ID,
            'payment_success': False,
        }
    )

@login_required
def success(request):
    booking_obj = get_object_or_404(
        Booking,
        id=request.session.get('booking_id'),
        user=request.user
    )
    return render(request, 'travelapp/success.html', {'booking': booking_obj})


@login_required
def receipt(request, booking_id):
    booking_obj = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'travelapp/receipt.html', {'booking': booking_obj})


@login_required
def e_ticket(request, booking_id):
    booking_obj = get_object_or_404(Booking, id=booking_id, user=request.user)
    ticket_qr = make_ticket_qr(booking_obj)

    return render(request, "travelapp/e_ticket.html", {
        "booking": booking_obj,
        "ticket_qr": ticket_qr
    })


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_on')
    return render(request, 'travelapp/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, id):
    booking_obj = get_object_or_404(Booking, id=id, user=request.user)

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()

        booking_obj.status = "Refund Processing"
        booking_obj.refund_status = "Processing"
        booking_obj.refund_amount = booking_obj.total_amount
        booking_obj.refund_requested_on = timezone.now()
        booking_obj.cancellation_reason = reason
        booking_obj.save()

        messages.success(
            request,
            f"Cancellation request submitted successfully. Refund of ₹{booking_obj.refund_amount} is now processing."
        )

        return redirect("my_bookings")

    return redirect("my_bookings")


@login_required
def toggle_wishlist(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    item, created = Wishlist.objects.get_or_create(user=request.user, package=package)

    if not created:
        item.delete()

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('package')
    return render(request, 'travelapp/wishlist.html', {'items': items})


def trip_planner(request):
    seed_data()

    packages = Package.objects.filter(is_active=True).select_related("category")
    recommended = None

    budget = request.GET.get("budget", "").strip()
    days = request.GET.get("days", "").strip()
    category = request.GET.get("category", "").strip()

    if budget or days or category:
        recommended = packages

        if budget.isdigit():
            recommended = recommended.filter(price__lte=int(budget))

        if days.isdigit():
            recommended = recommended.filter(days__lte=int(days))

        if category:
            recommended = recommended.filter(
                Q(category__slug=category) |
                Q(tags__icontains=category) |
                Q(category__name__icontains=category)
            )

        recommended = recommended.order_by("-is_featured", "price", "-rating")

    return render(request, "travelapp/trip_planner.html", {
        "categories": Category.objects.all(),
        "recommended": recommended,
        "budget": budget,
        "days": days,
        "selected_category": category,
    })




def contact(request):
    seed_data()

    packages = Package.objects.filter(is_active=True).order_by("name")

    if request.method == "POST":
        package_id = request.POST.get("package")
        package_obj = None

        if package_id:
            package_obj = Package.objects.filter(id=package_id).first()

        ContactEnquiry.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message"),
            package=package_obj,
        )

        messages.success(request, "Your enquiry has been submitted successfully. Our team will contact you soon.")
        return redirect("contact")

    return render(request, "travelapp/contact.html", {"packages": packages})



def blog_details(request, slug):
    seed_data()
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    related = BlogPost.objects.filter(is_published=True).exclude(id=post.id)[:3]

    return render(request, "travelapp/blog_details.html", {
        "post": post,
        "related": related
    })

@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    total_revenue = Payment.objects.filter(
        payment_status="Success"
    ).aggregate(total=Sum("amount"))["total"] or 0

    stats = {
        "users": User.objects.count(),
        "packages": Package.objects.count(),
        "bookings": Booking.objects.count(),
        "revenue": total_revenue,
    }

    users = User.objects.all().order_by("-date_joined")
    bookings = Booking.objects.select_related("user", "package").order_by("-booked_on")
    payments = Payment.objects.select_related("booking", "booking__package").order_by("-paid_on")
    refunds = Booking.objects.filter(
        refund_status__in=["Requested", "Processing", "Completed"]
    ).select_related("user", "package").order_by("-refund_requested_on")

    popular = Package.objects.annotate(count=Count("bookings")).order_by("-count")[:8]

    return render(request, "travelapp/dashboard.html", {
        "stats": stats,
        "users": users,
        "bookings": bookings,
        "payments": payments,
        "refunds": refunds,
        "popular": popular,
    })
    
    # ==========================
# USER PROFILE
# ==========================

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).count()

    total_spent = Booking.objects.filter(
        user=request.user
    ).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    return render(
        request,
        "travelapp/profile.html",
        {
            "bookings_count": bookings,
            "total_spent": total_spent,
        }
    )


# ==========================
# PACKAGE MANAGEMENT
# ==========================

@user_passes_test(lambda u: u.is_staff)
def admin_add_package(request):

    messages.success(request, "Package management feature enabled.")
    return redirect("dashboard")


@user_passes_test(lambda u: u.is_staff)
def admin_edit_package(request, id):

    messages.success(request, f"Edit Package #{id}")
    return redirect("dashboard")


@user_passes_test(lambda u: u.is_staff)
def admin_delete_package(request, id):

    package = get_object_or_404(Package, id=id)

    package.delete()

    messages.success(
        request,
        "Package deleted successfully."
    )

    return redirect("dashboard")


# ==========================
# BOOKING STATUS MANAGEMENT
# ==========================

@user_passes_test(lambda u: u.is_staff)
def admin_update_booking_status(request, id):

    booking = get_object_or_404(
        Booking,
        id=id
    )

    status = request.POST.get("status")

    if status:
        booking.status = status
        booking.save()

        messages.success(
            request,
            f"Booking TW-{booking.id} updated."
        )

    return redirect("dashboard")


# ==========================
# REFUND MANAGEMENT
# ==========================

@user_passes_test(lambda u: u.is_staff)
def admin_approve_refund(request, id):

    booking = get_object_or_404(
        Booking,
        id=id
    )

    booking.refund_status = "Processing"
    booking.status = "Refund Processing"
    booking.save()

    messages.success(
        request,
        "Refund approved."
    )

    return redirect("dashboard")


@user_passes_test(lambda u: u.is_staff)
def admin_reject_refund(request, id):

    booking = get_object_or_404(
        Booking,
        id=id
    )

    booking.refund_status = "Rejected"
    booking.save()

    messages.warning(
        request,
        "Refund rejected."
    )

    return redirect("dashboard")


@user_passes_test(lambda u: u.is_staff)
def admin_complete_refund(request, id):

    booking = get_object_or_404(
        Booking,
        id=id
    )

    booking.refund_status = "Completed"
    booking.status = "Refund Completed"
    booking.refund_completed_on = timezone.now()

    booking.save()

    messages.success(
        request,
        "Refund completed."
    )

    return redirect("dashboard")


# ==========================
# CONTACT ENQUIRY MANAGEMENT
# ==========================

@user_passes_test(lambda u: u.is_staff)
def admin_update_enquiry_status(request, id):

    enquiry = get_object_or_404(
        ContactEnquiry,
        id=id
    )

    status = request.POST.get("status")

    if status:
        enquiry.status = status
        enquiry.save()

    messages.success(
        request,
        "Enquiry updated."
    )

    return redirect("dashboard")