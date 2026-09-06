from django.contrib import admin
from .models import (
    Category, Package, Booking, Payment, Wishlist,
    Review, Coupon, ContactEnquiry, BlogPost
)


admin.site.site_header = "TravelWorld Admin"
admin.site.site_title = "TravelWorld"
admin.site.index_title = "Travel & Tourism Management"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "description")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        "name", "city", "country", "category", "price",
        "old_price", "days", "nights", "rating",
        "available_seats", "is_featured", "is_active",
    )

    list_filter = ("category", "country", "is_featured", "is_active", "rating")
    search_fields = ("name", "country", "city", "tags", "description")

    list_editable = ("price", "old_price", "is_featured", "is_active")
    readonly_fields = ("available_seats", "created_at")

    fieldsets = (
        ("Basic Package Details", {
            "fields": (
                "name", "country", "city", "category", "tags",
                "image", "description",
            )
        }),
        ("Pricing & Duration", {
            "fields": (
                "price", "old_price", "days", "nights",
                "seats", "available_seats",
            )
        }),
        ("Hotel, Flight & Rating", {
            "fields": ("hotel", "flight", "rating")
        }),
        ("Google Map Location", {
            "fields": ("map_query", "latitude", "longitude")
        }),
        ("Itinerary", {
            "fields": ("itinerary",)
        }),
        ("Display Settings", {
            "fields": ("is_featured", "is_active", "created_at")
        }),
    )


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ("amount", "payment_method", "upi_id", "transaction_id", "paid_on")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id", "full_name", "package", "travel_date",
        "members", "total_amount", "status",
        "refund_status", "refund_amount", "booked_on",
    )

    list_filter = ("status", "refund_status", "travel_date", "booked_on")
    search_fields = ("full_name", "email", "phone", "package__name", "coupon_code")
    list_editable = ("status", "refund_status")

    readonly_fields = (
        "user", "package", "full_name", "phone", "email",
        "travel_date", "members", "coupon_code", "discount_amount",
        "total_amount", "booked_on", "refund_requested_on",
    )

    actions = ("mark_confirmed", "mark_refund_processing", "mark_refund_completed")
    inlines = [PaymentInline]

    fieldsets = (
        ("Customer Details", {
            "fields": ("user", "full_name", "phone", "email")
        }),
        ("Booking Details", {
            "fields": ("package", "travel_date", "members", "status", "booked_on")
        }),
        ("Payment & Coupon Details", {
            "fields": ("coupon_code", "discount_amount", "total_amount")
        }),
        ("Refund Management", {
            "fields": (
                "refund_status", "refund_amount", "refund_requested_on",
                "refund_completed_on", "cancellation_reason",
            )
        }),
    )

    def mark_confirmed(self, request, queryset):
        queryset.update(status="Confirmed")
    mark_confirmed.short_description = "Mark selected bookings as Confirmed"

    def mark_refund_processing(self, request, queryset):
        queryset.update(status="Refund Processing", refund_status="Processing")
    mark_refund_processing.short_description = "Mark selected bookings as Refund Processing"

    def mark_refund_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(
            status="Refund Completed",
            refund_status="Completed",
            refund_completed_on=timezone.now()
        )
    mark_refund_completed.short_description = "Mark selected refunds as Completed"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "booking", "amount", "payment_method", "upi_id",
        "payment_status", "transaction_id", "paid_on",
    )

    list_filter = ("payment_status", "payment_method", "paid_on")
    search_fields = ("booking__full_name", "booking__package__name", "transaction_id", "upi_id")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "package", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "package__name")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "package", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "package__name", "comment")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "min_amount", "active")
    list_editable = ("discount_percent", "min_amount", "active")
    list_filter = ("active",)
    search_fields = ("code",)


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "subject", "package", "status", "created_at")
    list_filter = ("status", "created_at")
    list_editable = ("status",)
    search_fields = ("name", "email", "phone", "subject", "message")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "created_at")
    list_filter = ("category", "is_published", "created_at")
    search_fields = ("title", "short_description", "content")
    prepopulated_fields = {"slug": ("title",)}