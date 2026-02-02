import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grambazaar.settings')
django.setup()

from django.contrib.auth.models import User
from market.models import SHG, Product, DigiCourse, Order, LedgerEntry


def run():
    if SHG.objects.exists():
        print('Demo data already exists. Skipping.')
        return

    print('Creating demo users and SHGs...')
    shgs = []
    levels = ['bronze', 'silver', 'gold', 'silver']
    cities = ['Jaipur', 'Varanasi', 'Kochi', 'Bhopal']
    states = ['Rajasthan', 'Uttar Pradesh', 'Kerala', 'Madhya Pradesh']

    for i in range(4):
        user = User.objects.create_user(
            username=f'shg{i+1}',
            password='password123',
            email=f'shg{i+1}@demo.com',
        )
        shg = SHG.objects.create(
            user=user,
            name=f'SHG Collective {i+1}',
            contact_person=f'Leader {i+1}',
            phone=f'99900000{i+1}',
            email=user.email,
            state=states[i],
            city=cities[i],
            description='Demo Self Help Group for Grambazaar hackathon.',
            verification_level=levels[i],
            wallet_balance=Decimal('1000.00') * (i + 1),
        )
        shgs.append(shg)

    print('Creating demo products...')
    demo_products = [
        ('Handmade Jute Bag', 'Eco-friendly jute bag crafted by rural artisans.', 'handicrafts', Decimal('499.00'), 12),
        ('Organic Pickle Combo', 'Traditional homemade pickles from farm fresh produce.', 'food', Decimal('299.00'), 8),
        ('Handwoven Cotton Saree', 'Soft cotton saree woven on traditional looms.', 'textiles', Decimal('1299.00'), 5),
        ('Terracotta Tea Cups', 'Set of 6 eco-friendly terracotta cups.', 'pottery', Decimal('399.00'), 3),
        ('Beaded Necklace', 'Colorful handmade beaded necklace.', 'jewelry', Decimal('199.00'), 15),
        ('Millet Laddu Box', 'Healthy millet-based sweets.', 'food', Decimal('349.00'), 4),
        ('Bamboo Basket', 'Multi-purpose handcrafted bamboo basket.', 'handicrafts', Decimal('449.00'), 6),
        ('Spice Mix Pack', 'Assorted traditional spice mixes.', 'food', Decimal('249.00'), 9),
        ('Block Print Dupatta', 'Hand-block printed cotton dupatta.', 'textiles', Decimal('599.00'), 7),
        ('Clay Diyas Pack', 'Pack of 20 decorative diyas.', 'pottery', Decimal('199.00'), 20),
    ]

    for idx, (title, desc, cat, price, inv) in enumerate(demo_products):
        Product.objects.create(
            shg=shgs[idx % len(shgs)],
            title=title,
            description=desc,
            price=price,
            category=cat,
            inventory=inv,
            status='live',
        )

    print('Creating DigiLearner demo courses...')
    DigiCourse.objects.create(
        title='How to Photograph Your Products With a Phone',
        video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        language='english',
        description='Simple tips for better product photos using basic phones.',
    )
    DigiCourse.objects.create(
        title='Pricing Products for Online Marketplaces',
        video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        language='hindi',
        description='Understanding cost, margin and competitive pricing.',
    )

    print('Creating sample orders and ledger entries...')
    first_product = Product.objects.first()
    order = Order.objects.create(
        product=first_product,
        buyer_name='Demo Buyer',
        buyer_contact='9876543210',
        address='Demo address for hackathon flow.',
        amount=first_product.price,
        status='approved',
    )

    shg = first_product.shg
    LedgerEntry.objects.create(
        shg=shg,
        date=order.created_at.date(),
        description=f'Order {order.id} payout',
        credit=order.amount,
        debit=Decimal('0.00'),
        balance_after=shg.wallet_balance + order.amount,
    )

    print('Demo data created successfully.')


if __name__ == '__main__':
    run()
