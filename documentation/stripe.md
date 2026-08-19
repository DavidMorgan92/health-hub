# Stripe checkout

Set the Stripe secret key in the environment before starting Django:

```powershell
$env:STRIPE_SECRET_KEY = 'sk_test_...'
python manage.py runserver
```

The checkout page creates Stripe Checkout line items from the server-side cart. Plans use `subscription` mode with a recurring monthly price. One-time products use `payment` mode. If a cart contains both, Stripe uses subscription mode: the plan recurs monthly and the products are charged once on the initial invoice.

The success and cancellation URLs are configured for the current request host. Fulfilment, stock reduction, and subscription state should be handled with a verified Stripe webhook before going live.