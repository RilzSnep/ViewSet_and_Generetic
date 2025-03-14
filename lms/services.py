import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def check_stripe_session(session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка проверки сессии в Stripe: {str(e)}")


def create_stripe_product(course):
    """
    Создаёт продукт в Stripe на основе курса.
    """
    try:
        product = stripe.Product.create(
            name=course.title,
            description=course.description,
        )
        return product
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания продукта в Stripe: {str(e)}")


def create_stripe_price(course, product_id):
    """
    Создаёт цену для продукта в Stripe.
    """
    try:
        # Stripe принимает цену в копейках (умножаем на 100)
        price_in_cents = int(course.price * 100)
        price = stripe.Price.create(
            product=product_id,
            unit_amount=price_in_cents,
            currency='usd',  # Валюта (для тестов используем USD)
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания цены в Stripe: {str(e)}")


def create_stripe_checkout_session(user, course, price_id):
    """
    Создаёт сессию оплаты в Stripe.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://127.0.0.1:8000/success/',
            cancel_url='http://127.0.0.1:8000/cancel/',
            customer_email=user.email,
        )
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания сессии оплаты в Stripe: {str(e)}")
