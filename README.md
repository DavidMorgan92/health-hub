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

#### Product images on Heroku

Heroku's local filesystem is temporary, so production uploads must use persistent object storage. Local development continues to use `media/`, while production can use either the Bucketeer add-on or a separately managed Amazon S3 bucket.

The simplest Heroku setup is Bucketeer, which provisions an S3 bucket and adds these config vars automatically:

```text
heroku addons:create bucketeer:hobbyist
```

Bucketeer provides the following config vars, which this project reads automatically:

- `BUCKETEER_BUCKET_NAME`: the S3 bucket name
- `BUCKETEER_AWS_ACCESS_KEY_ID`: the bucket access key
- `BUCKETEER_AWS_SECRET_ACCESS_KEY`: the bucket secret key
- `BUCKETEER_AWS_REGION`: the bucket's AWS region

For a separately managed S3 bucket, set the equivalent `AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_S3_REGION_NAME` config vars instead. The bucket must allow authenticated `GetObject` requests.

After provisioning storage, redeploy and upload the images again; files previously written to the Heroku filesystem cannot be recovered after a dyno restart.

## Testing

[Testing documentation](TESTING.md)
