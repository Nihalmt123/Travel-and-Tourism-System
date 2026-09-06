from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=20, default='🌍')
    description = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.name


class Package(models.Model):
    name = models.CharField(max_length=120)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='packages')
    tags = models.CharField(max_length=255)
    image = models.URLField(max_length=600)
    price = models.PositiveIntegerField(default=20000)
    old_price = models.PositiveIntegerField(null=True, blank=True)
    days = models.PositiveIntegerField(default=5)
    nights = models.PositiveIntegerField(default=4)
    hotel = models.CharField(max_length=200, default='Premium Hotel')
    flight = models.CharField(max_length=200, default='Flight assistance available')
    rating = models.FloatField(default=4.5)
    seats = models.PositiveIntegerField(default=30)
    description = models.TextField()
    itinerary = models.TextField(blank=True)
    map_query = models.CharField(max_length=250, blank=True)
    latitude = models.CharField(max_length=50, blank=True)
    longitude = models.CharField(max_length=50, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def available_seats(self):
        booked = self.bookings.exclude(
            status__in=['Cancelled', 'Refund Processing', 'Refund Completed']
        ).aggregate(total=models.Sum('members'))['total'] or 0
        return max(self.seats - booked, 0)


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Payment Done', 'Payment Done'),
        ('Confirmed', 'Confirmed'),
        ('Travel Scheduled', 'Travel Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Refund Processing', 'Refund Processing'),
        ('Refund Completed', 'Refund Completed'),
    ]

    REFUND_STATUS = [
        ('Not Requested', 'Not Requested'),
        ('Requested', 'Requested'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='bookings')
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    travel_date = models.DateField()
    members = models.PositiveIntegerField(default=1)
    coupon_code = models.CharField(max_length=40, blank=True)
    discount_amount = models.PositiveIntegerField(default=0)
    total_amount = models.PositiveIntegerField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    booked_on = models.DateTimeField(default=timezone.now)

    refund_status = models.CharField(max_length=30, choices=REFUND_STATUS, default='Not Requested')
    refund_amount = models.PositiveIntegerField(default=0)
    refund_requested_on = models.DateTimeField(null=True, blank=True)
    refund_completed_on = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.full_name} - {self.package.name}'


class Payment(models.Model):
    STATUS = [('Pending', 'Pending'), ('Success', 'Success'), ('Failed', 'Failed')]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=50, default='UPI QR')
    upi_id = models.CharField(max_length=100, default='nihal8129587568-1@okaxis')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=20, choices=STATUS, default='Pending')
    paid_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.booking.full_name} - {self.payment_status}'


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'package')


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.package.name} - {self.rating}'


class Coupon(models.Model):
    code = models.CharField(max_length=40, unique=True)
    discount_percent = models.PositiveIntegerField(default=10)
    min_amount = models.PositiveIntegerField(default=20000)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class ContactEnquiry(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Contacted', 'Contacted'),
        ('Closed', 'Closed'),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='New')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    image = models.URLField(max_length=600)
    category = models.CharField(max_length=80, default='Travel Guide')
    short_description = models.CharField(max_length=250)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title