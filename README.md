# Health Hub

Health Hub is a web application that provides a store front for users to purchase products and equipment to reach their health and fitness goals. It also allows them to purchase, on a subscription basis, plans for exercise and nutrition so they can have instruction on how to achieve their goals.

## UX/UI

- [User Stories](documentation/user-stories.md)
- [Wireframes](documentation/wireframes/wireframes.md)

## Deployment

- [Configuring Stripe](documentation/stripe.md)

### Heroku

The application uses SQLite locally and switches to PostgreSQL automatically when
Heroku provides the `DATABASE_URL` config var. Add the following config vars in
Heroku, replacing the example values:

```text
SECRET_KEY=<a-long-random-value>
DEBUG=False
ALLOWED_HOSTS=<your-app-name>.herokuapp.com
STRIPE_SECRET_KEY=<your-stripe-secret-key>
STRIPE_WEBHOOK_SECRET=<your-stripe-webhook-secret>
```

Attach a Heroku Postgres database to populate `DATABASE_URL`. The `release` process
in the `Procfile` runs migrations automatically before each new release.

## Testing

Invoke `python manage.py test` at the project root to run the automated test suite.
