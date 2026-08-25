# Stripe checkout

## Development

1. In the project root, copy `.env.example` to `.env`.
2. Set the Stripe test secret key in `.env`:

```env
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

Use the test-mode secret key from the [Stripe Dashboard API keys](https://dashboard.stripe.com/test/apikeys) page. Do not commit `.env`; it is already excluded by `.gitignore`.

Use the webhook signing secret from the Stripe Workbench webhook endpoint configuration. It starts with `whsec_` and is used by Django to verify that incoming subscription events came from Stripe.

Install the project dependencies and start Django:

```powershell
python -m pip install -r Requirements.txt
python manage.py runserver
```

The settings load `.env` automatically when Django starts. As an alternative, a temporary PowerShell environment variable can be used for one terminal session:

```powershell
$env:STRIPE_SECRET_KEY = 'sk_test_your_key_here'
$env:STRIPE_WEBHOOK_SECRET = 'whsec_your_webhook_secret_here'
python manage.py runserver
```

For local webhook testing, forward Stripe events to the Django endpoint with the Stripe CLI:

```powershell
stripe listen --forward-to http://127.0.0.1:8000/subscriptions/stripe/webhook/
```

Use the `whsec_...` value printed by `stripe listen` as `STRIPE_WEBHOOK_SECRET` for that local session.

Use Stripe test card details while developing. Test keys and test cards must not be used for real payments.

## Production

Configure `STRIPE_SECRET_KEY` as a secret environment variable in the hosting provider or process manager. Use the live secret key from the [Stripe Dashboard API keys](https://dashboard.stripe.com/apikeys) page:

```text
STRIPE_SECRET_KEY=sk_live_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret_here
```

Do not upload `.env`, place the key in source control, or expose it in browser code. Restart or redeploy the application after changing the variable so Django reloads the configuration. Confirm that production uses `DEBUG=False` and HTTPS before accepting live payments.

Configure a Stripe webhook endpoint for `/subscriptions/stripe/webhook/` and use its signing secret as `STRIPE_WEBHOOK_SECRET`. Keep test and live webhook secrets separate.

The application currently uses `gbp` as `STRIPE_CURRENCY`. Change that setting before deployment if the store should charge in another currency.

The checkout page creates Stripe Checkout line items from the server-side cart. Plans use `subscription` mode with a recurring monthly price. One-time products use `payment` mode. If a cart contains both, Stripe uses subscription mode: the plan recurs monthly and the products are charged once on the initial invoice.

The success and cancellation URLs are configured for the current request host. Fulfilment, stock reduction, and subscription state should be handled with a verified Stripe webhook before going live. Never fulfil an order based only on the browser redirect.