TravelWorld Advanced Modified Project

Included updates:
1. Smart search like travel websites: exact place result comes first, then city/country/category/tag matches.
2. Admin can add unlimited packages from Django Admin.
3. Separate package categories: Honeymoon, Nature, Adventure, Beach, Family, Pilgrimage, Luxury, Wildlife.
4. Search filters: destination/category/theme and maximum budget.
5. Payment page with UPI ID: nihal8129587568-1@okaxis.
6. Dynamic UPI QR generation with exact booking amount, for example 20000 automatically added to QR.
7. Your uploaded QR image is included as static fallback.
8. More beautiful modern standard UI.
9. Professional receipt with print/save PDF button.
10. My Trips page with booking tracker.
11. Wishlist, coupons and admin dashboard.

Commands:
cd travelproject
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_travel
python manage.py createsuperuser
python manage.py runserver

Open:
http://127.0.0.1:8000/

Important:
For the QR amount to come automatically while scanning, install requirements.txt because dynamic QR uses qrcode and Pillow.
