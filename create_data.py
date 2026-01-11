import os
import django
import random
from django.utils import timezone

# Cấu hình môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booktourapi.settings')
django.setup()

from django.contrib.auth.models import User
from tourservice.models import UserProfile, Service, Booking, Review


def create_dummy_data():
    print("Đang xóa dữ liệu cũ...")
    # Xóa theo thứ tự để tránh lỗi khóa ngoại
    Review.objects.all().delete()
    Booking.objects.all().delete()
    Service.objects.all().delete()
    # Xóa user thường, giữ lại superuser
    User.objects.exclude(is_superuser=True).delete()

    print("Đang tạo Users...")

    # --- Helper function để update profile thay vì create ---
    def create_user_with_profile(username, email, password, role, is_verified=False):
        user = User.objects.create_user(username=username, email=email, password=password)
        # Vì signals.py đã tự tạo profile, ta chỉ cần lấy ra và update
        profile = UserProfile.objects.get(user=user)
        profile.role = role
        profile.is_verified = is_verified
        profile.save()
        return user

    # 1. Tạo Provider
    provider1 = create_user_with_profile('provider1', 'p1@test.com', '123', 'PROVIDER', True)
    provider2 = create_user_with_profile('provider2', 'p2@test.com', '123', 'PROVIDER', False)

    # 2. Tạo Customer
    customer = create_user_with_profile('customer1', 'c1@test.com', '123', 'CUSTOMER')

    print("Đang tạo Services (Tour/Khách sạn)...")
    locations = ['Đà Lạt', 'Hà Nội', 'Hồ Chí Minh', 'Đà Nẵng', 'Phú Quốc']
    types = ['TOUR', 'HOTEL', 'VEHICLE']

    services = []
    for i in range(10):
        svc = Service.objects.create(
            provider=provider1,
            name=f"Dịch vụ Du lịch {locations[i % 5]} #{i + 1}",
            description="Mô tả dịch vụ trải nghiệm tuyệt vời...",
            price=random.randint(500000, 5000000),
            location=locations[i % 5],
            service_type=random.choice(types),
            capacity=20,
            active=True
        )
        services.append(svc)

    print("Đang tạo Bookings & Reviews...")
    for svc in services:
        # Tạo Booking
        for _ in range(random.randint(1, 5)):
            Booking.objects.create(
                customer=customer,
                service=svc,
                quantity=random.randint(1, 4),
                total_price=svc.price * 2,
                status='CONFIRMED'
            )

        # Tạo Review
        Review.objects.create(
            customer=customer,
            service=svc,
            rating=random.randint(3, 5),
            comment="Dịch vụ rất tốt, sẽ quay lại!"
        )

    print("=== HOÀN TẤT! ===")
    print("Tài khoản test:")
    print(" - Provider (Đã duyệt): provider1 / 123")
    print(" - Provider (Chưa duyệt): provider2 / 123")
    print(" - Customer: customer1 / 123")


if __name__ == '__main__':
    create_dummy_data()