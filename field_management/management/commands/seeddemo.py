"""Seed the database with demo content."""
from __future__ import annotations

from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from addons.models import AddOn
from field_booking.models import Booking, Payment
from field_management.constants import CATEGORY_DEFINITIONS
from field_management.models import Category, Venue, VenueAvailability
from user_interactions.models import Review, Wishlist


CATEGORY_ADDONS: dict[str, list[tuple[str, str, Decimal]]] = {
    "badminton": [
        (
            "Shuttlecock premium (Tube)",
            "Satu tube berisi 12 shuttlecock bulu angsa turnamen.",
            Decimal("55000"),
        ),
        (
            "Sewa raket badminton",
            "Paket dua raket karbon siap pakai dengan tas pelindung.",
            Decimal("40000"),
        ),
        (
            "Sewa net turnamen",
            "Pemasangan net standar BWF untuk satu lapangan.",
            Decimal("30000"),
        ),
        (
            "Grip pengganti",
            "Set grip anti-slip baru untuk dua raket.",
            Decimal("15000"),
        ),
        (
            "Jasa fotografer",
            "Fotografer profesional untuk mendokumentasikan permainan Anda.",
            Decimal("400000"),
        ),
        (
            "Wasit badminton",
            "Wasit berlisensi untuk pertandingan kompetitif.",
            Decimal("200000"),
        ),
    ],
    "basket": [
        (
            "Bola basket (sewa)",
            "Satu bola indoor komposit siap bertanding.",
            Decimal("50000"),
        ),
        (
            "Rompi tim (2 set)",
            "Rompi dua warna untuk membedakan tim selama scrimmage.",
            Decimal("50000"),
        ),
        (
            "Papan skor & operator",
            "Operator profesional berikut papan skor dan shot clock digital.",
            Decimal("150000"),
        ),
        (
            "Wasit basket (2 orang)",
            "Dua wasit berlisensi untuk mengawal jalannya pertandingan.",
            Decimal("500000"),
        ),
        (
            "Sepatu basket (sewa)",
            "Sewa sepasang sepatu basket premium.",
            Decimal("50000"),
        ),
        (
            "Fotografer/Videografer",
            "Dokumentasi foto dan video profesional pertandingan.",
            Decimal("500000"),
        ),
    ],
    "billiard": [
        (
            "Stik premium (sewa)",
            "Sewa stik berkualitas turnamen dengan perawatan rutin.",
            Decimal("50000"),
        ),
        (
            "Kapur cue",
            "Satu kotak kapur cue profesional.",
            Decimal("15000"),
        ),
        (
            "Sarung tangan billiard",
            "Sarung tangan microfiber anti-slip.",
            Decimal("25000"),
        ),
        (
            "Jasa wasit/marker",
            "Pengawas pertandingan untuk menjaga jalannya game.",
            Decimal("50000"),
        ),
        (
            "Pelatih billiard",
            "Sesi pelatih profesional per jam.",
            Decimal("150000"),
        ),
    ],
    "futsal": [
        (
            "Bola futsal (sewa)",
            "Sewa bola futsal standar pertandingan.",
            Decimal("50000"),
        ),
        (
            "Rompi tim (2 set)",
            "Rompi latihan dua warna untuk dua tim.",
            Decimal("50000"),
        ),
        (
            "Sarung tangan kiper",
            "Sewa sarung tangan kiper profesional.",
            Decimal("30000"),
        ),
        (
            "Sepatu futsal (sewa)",
            "Pilihan ukuran lengkap sepatu futsal premium.",
            Decimal("40000"),
        ),
        (
            "Papan skor digital",
            "Papan skor digital portabel untuk menghitung skor real-time.",
            Decimal("75000"),
        ),
        (
            "Wasit futsal",
            "Wasit profesional untuk memimpin pertandingan.",
            Decimal("200000"),
        ),
        (
            "Fotografer",
            "Fotografer olahraga untuk dokumentasi pertandingan.",
            Decimal("400000"),
        ),
    ],
    "mini-soccer": [
        (
            "Bola mini soccer (sewa)",
            "Sewa bola mini soccer berkualitas match day.",
            Decimal("60000"),
        ),
        (
            "Rompi tim (2 set)",
            "Rompi latihan dua warna untuk membedakan tim.",
            Decimal("60000"),
        ),
        (
            "Sarung tangan kiper",
            "Sewa sarung tangan kiper profesional.",
            Decimal("30000"),
        ),
        (
            "Sepatu mini soccer (sewa)",
            "Sewa sepatu turf untuk permukaan rumput sintetis.",
            Decimal("40000"),
        ),
        (
            "Papan skor",
            "Papan skor portabel untuk pertandingan Anda.",
            Decimal("100000"),
        ),
        (
            "Wasit mini soccer",
            "Wasit profesional untuk memimpin pertandingan.",
            Decimal("250000"),
        ),
        (
            "Fotografer/Videografer",
            "Dokumentasi foto dan video profesional.",
            Decimal("500000"),
        ),
    ],
    "padel": [
        (
            "Bola padel (kaleng)",
            "Satu kaleng berisi tiga bola padel premium.",
            Decimal("90000"),
        ),
        (
            "Raket padel (sewa)",
            "Sewa raket padel grafit dengan grip baru.",
            Decimal("60000"),
        ),
        (
            "Pelatih padel",
            "Pelatih/partner tanding profesional per jam.",
            Decimal("200000"),
        ),
        (
            "Fotografer",
            "Fotografer olahraga untuk dokumentasi pertandingan.",
            Decimal("400000"),
        ),
    ],
    "sepak-bola": [
        (
            "Bola sepak (sewa)",
            "Sewa bola pertandingan standar FIFA.",
            Decimal("75000"),
        ),
        (
            "Rompi latihan (2 set)",
            "Rompi latihan dua warna untuk sesi drill.",
            Decimal("75000"),
        ),
        (
            "Sarung tangan kiper",
            "Sewa sarung tangan kiper profesional.",
            Decimal("40000"),
        ),
        (
            "Cone & marker latihan",
            "Satu set cone dan marker untuk latihan taktik.",
            Decimal("50000"),
        ),
        (
            "Wasit sepak bola (3 orang)",
            "Tim wasit lengkap (referee + 2 asisten).",
            Decimal("1000000"),
        ),
        (
            "Tim medis/P3K",
            "Tim medis profesional berikut peralatan P3K.",
            Decimal("300000"),
        ),
        (
            "Fotografer/Videografer",
            "Paket dokumentasi profesional foto dan video.",
            Decimal("700000"),
        ),
    ],
    "tenis-meja": [
        (
            "Bola pingpong (kotak)",
            "Satu kotak bola seluloid turnamen.",
            Decimal("30000"),
        ),
        (
            "Bet tenis meja (sewa)",
            "Sewa dua bet karet profesional.",
            Decimal("20000"),
        ),
        (
            "Robot pelontar bola",
            "Sewa robot pelontar bola per jam.",
            Decimal("75000"),
        ),
        (
            "Wasit/Penghitung skor",
            "Wasit sekaligus penghitungan skor per jam.",
            Decimal("50000"),
        ),
        (
            "Pelatih tenis meja",
            "Pelatih atau sparring partner profesional per jam.",
            Decimal("150000"),
        ),
    ],
    "tennis": [
        (
            "Bola tenis (kaleng)",
            "Kaleng isi tiga bola tenis premium.",
            Decimal("80000"),
        ),
        (
            "Raket tenis (sewa)",
            "Sewa raket grafit siap tanding.",
            Decimal("50000"),
        ),
        (
            "Mesin pelontar bola",
            "Mesin pelontar otomatis per jam.",
            Decimal("100000"),
        ),
        (
            "Pemungut bola",
            "Ball boy/girl per jam untuk membantu latihan.",
            Decimal("50000"),
        ),
        (
            "Pelatih tenis",
            "Pelatih atau partner tanding profesional per jam.",
            Decimal("200000"),
        ),
        (
            "Fotografer",
            "Fotografer olahraga untuk mendokumentasikan sesi Anda.",
            Decimal("400000"),
        ),
    ],
    "volly-ball": [
        (
            "Bola voli (sewa)",
            "Sewa bola voli standar turnamen.",
            Decimal("40000"),
        ),
        (
            "Net turnamen (sewa)",
            "Sewa net voli standar turnamen lengkap dengan tiang.",
            Decimal("50000"),
        ),
        (
            "Papan skor digital",
            "Papan skor digital dengan operator.",
            Decimal("75000"),
        ),
        (
            "Wasit voli",
            "Wasit profesional untuk pertandingan resmi.",
            Decimal("250000"),
        ),
        (
            "Pelindung lutut & lengan",
            "Sewa pelindung lutut dan lengan untuk dua pemain.",
            Decimal("25000"),
        ),
        (
            "Fotografer",
            "Fotografer profesional untuk dokumentasi laga.",
            Decimal("400000"),
        ),
    ],
}

DEFAULT_ADDONS: list[tuple[str, str, Decimal]] = [
    (
        "Premium lighting",
        "Enhanced lighting package for night matches",
        Decimal("50000"),
    ),
    (
        "Professional referee",
        "Certified referee service for competitive games",
        Decimal("150000"),
    ),
]


class Command(BaseCommand):
    help = "Populate the database with demo venues, users, and bookings."

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("Resetting demo data...")
            self._create_admin()
            user = self._create_demo_user()
            venues = self._create_catalog()
            self._create_bookings(user, venues)
        self.stdout.write(self.style.SUCCESS("Demo data ready. You can log in with 'demo' / 'Demo123!'"))

    def _create_admin(self):
        user_model = get_user_model()
        if not user_model.objects.filter(is_staff=True).exists():
            admin = user_model.objects.create_user(
                "admin", password="Admin123!", is_staff=True, is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS("Created default admin account: admin / Admin123!"))
        else:
            self.stdout.write("Admin account already present. Skipping creation.")

    def _create_demo_user(self):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(username="demo")
        if created:
            user.set_password("Demo123!")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: demo / Demo123!"))
        return user

    def _create_catalog(self) -> list[Venue]:
        category_objs = {}
        for slug, name in CATEGORY_DEFINITIONS:
            category, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
            if category.name != name:
                category.name = name
                category.save(update_fields=["name"])
            category_objs[slug] = category

        venue_specs = [
            {
                "name": "Skyline Futsal Dome",
                "category": category_objs["futsal"],
                "description": "Premium futsal court with climate control, smart lighting, and professional-grade turf.",
                "location": "Central Jakarta",
                "city": "Jakarta",
                "address": "Jl. Merdeka No. 123, Jakarta",
                "price_per_hour": Decimal("350000"),
                "capacity": 12,
                "facilities": "Locker room,Shower,Lounge,Parking",
                "image_url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?auto=format&fit=crop&w=800&q=80",
            },
            {
                "name": "Aurora Hoops Pavilion",
                "category": category_objs["basket"],
                "description": "Glass-roofed basketball court with viewing gallery and digital scoreboard.",
                "location": "Bandung",
                "city": "Bandung",
                "address": "Jl. Braga No. 88, Bandung",
                "price_per_hour": Decimal("420000"),
                "capacity": 20,
                "facilities": "Changing rooms,Café,Parking,Equipment rental",
                "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80",
            },
            {
                "name": "Featherlite Badminton Hub",
                "category": category_objs["badminton"],
                "description": "Tournament-ready badminton complex with cushioned floors and LED panel lighting.",
                "location": "Yogyakarta",
                "city": "Yogyakarta",
                "address": "Jl. Malioboro No. 17, Yogyakarta",
                "price_per_hour": Decimal("250000"),
                "capacity": 8,
                "facilities": "Locker room,Equipment store,Cafeteria,Wi-Fi",
                "image_url": "https://images.unsplash.com/photo-1601288496920-b6154fe362d7?auto=format&fit=crop&w=800&q=80",
            },
        ]

        created_venues: list[Venue] = []
        for spec in venue_specs:
            venue, _ = Venue.objects.update_or_create(
                slug=slugify(spec["name"]),
                defaults=spec,
            )
            created_venues.append(venue)
            self._ensure_addons(venue)
            self._ensure_availability(venue)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_venues)} venues."))
        return created_venues

    def _ensure_addons(self, venue: Venue):
        category_slug = getattr(venue.category, "slug", "") or ""
        addons = CATEGORY_ADDONS.get(category_slug, DEFAULT_ADDONS)
        keep_names = [name for name, *_ in addons]

        # Remove stale add-ons that are no longer part of the curated list.
        venue.addons.exclude(name__in=keep_names).delete()

        for name, description, price in addons:
            AddOn.objects.update_or_create(
                venue=venue,
                name=name,
                defaults={"description": description, "price": price},
            )

    def _ensure_availability(self, venue: Venue):
        VenueAvailability.objects.filter(venue=venue).delete()
        base = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        for day_offset in range(3):
            start = base + timedelta(days=day_offset)
            end = start + timedelta(hours=3)
            VenueAvailability.objects.create(venue=venue, start_datetime=start, end_datetime=end)

    def _create_bookings(self, user, venues: list[Venue]):
        if not venues:
            return
        base_date = timezone.localdate() + timedelta(days=1)
        start = timezone.make_aware(datetime.combine(base_date, time(hour=9)))
        end = start + timedelta(hours=2)
        booking, created = Booking.objects.get_or_create(
            user=user,
            venue=venues[0],
            start_datetime=start,
            end_datetime=end,
            defaults={"notes": "Friendly scrimmage with the neighbourhood team."},
        )
        if not created:
            booking.notes = "Friendly scrimmage with the neighbourhood team."
            booking.save(update_fields=["notes", "updated_at"])
        booking.addons.set(list(booking.venue.addons.all()[:1]))
        Payment.objects.update_or_create(
            booking=booking,
            defaults={
                "method": "qris",
                "status": "confirmed",
                "total_amount": booking.total_cost,
                "deposit_amount": Decimal("10000"),
                "reference_code": "VS-DEMO-0001",
            },
        )
        Review.objects.update_or_create(
            user=user,
            venue=booking.venue,
            defaults={
                "rating": 5,
                "comment": "Fantastic facility with spotless amenities and friendly staff!",
            },
        )
        Wishlist.objects.get_or_create(user=user, venue=booking.venue)
        self.stdout.write(self.style.SUCCESS("Sample booking, payment, and review are ready."))
