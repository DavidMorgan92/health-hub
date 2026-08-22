# Stripe checkout

## Development

1. In the project root, copy `.env.example` to `.env`.
2. Set the Stripe test secret key in `.env`:

```env
STRIPE_SECRET_KEY=sk_test_your_key_here
```

Use the test-mode secret key from the [Stripe Dashboard API keys](https://dashboard.stripe.com/test/apikeys) page. Do not commit `.env`; it is already excluded by `.gitignore`.

Install the project dependencies and start Django:

```powershell
python -m pip install -r Requirements.txt
python manage.py runserver
```

The settings load `.env` automatically when Django starts. As an alternative, a temporary PowerShell environment variable can be used for one terminal session:

```powershell
$env:STRIPE_SECRET_KEY = 'sk_test_your_key_here'
python manage.py runserver
```

Use Stripe test card details while developing. Test keys and test cards must not be used for real payments.

## Production

Configure `STRIPE_SECRET_KEY` as a secret environment variable in the hosting provider or process manager. Use the live secret key from the [Stripe Dashboard API keys](https://dashboard.stripe.com/apikeys) page:

```text
STRIPE_SECRET_KEY=sk_live_your_key_here
```

Do not upload `.env`, place the key in source control, or expose it in browser code. Restart or redeploy the application after changing the variable so Django reloads the configuration. Confirm that production uses `DEBUG=False` and HTTPS before accepting live payments.

The application currently uses `gbp` as `STRIPE_CURRENCY`. Change that setting before deployment if the store should charge in another currency.

The checkout page creates Stripe Checkout line items from the server-side cart. Plans use `subscription` mode with a recurring monthly price. One-time products use `payment` mode. If a cart contains both, Stripe uses subscription mode: the plan recurs monthly and the products are charged once on the initial invoice.

The success and cancellation URLs are configured for the current request host. Fulfilment, stock reduction, and subscription state should be handled with a verified Stripe webhook before going live. Never fulfil an order based only on the browser redirect.