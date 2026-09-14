# Testing

## Automated test suite

Invoke `python manage.py test` at the project root to run the automated test suite.

## Manual testing

### Access control

There are routes which should only be accessed by authenticated users.

Then there are routes which should only be accessed by unauthenticated users.

Then there are routes which should only be accessed by authenticated admin users.

I will test this validity.

#### Authenticated users only

<details>
  <summary>Plans home page</summary>
  <p>The plans home page is for an authenticated user to view and manage their subscribed plans. An unauthenticated user has no purpose for this page.</p>
  <p>I have confirmed that when attempting to access the plans route as an unauthenticated user I am redirected to the login page.</p>
</details>

<details>
  <summary>Plan details page</summary>
  <p>The plan details page is for an authenticated user to see a plan details only if they have an active subscription to it. An unauthenticated user has no purpose for this page.</p>
  <p>I have confirmed that when attempting to access the plans/8 route as an unauthenticated user I am redirected to the login page.</p>
</details>

<details>
  <summary>Logout page</summary>
  <p>The logout page is for an authenticated user to logout. An unauthenticated user has no purpose for this page.</p>
  <p>I have confirmed that when attempting to access the accounts/logout route as an unauthenticated user I am redirected to the home page.</p>
</details>

<details>
  <summary>Checkout page with plans in cart</summary>
  <p>Plans must be associated with an account when purchasing. An unauthenticated user should not be able to purchase plans. The expected flow is that when the checkout page is reached and the user has plans in the basket, if they are unauthenticated they will be required to log in, and then be redirected to continue the checkout.</p>
  <p>I have confirmed that when attempting to purchase a plan as an unauthenticated user I am required to log in, and upon login I am redirected to continue the checkout.</p>
  <p>I have also confirmed that I am not required to log in as an unauthenticated user if there are only products in the basket, and no plans.</p>
</details>

#### Unauthenticated users only

<details>
  <summary>Login page</summary>
  <p>The login page is for unauthenticated users to log in. An authenticated user has no purpose for this page.</p>
  <p>I have confirmed that when I navigate to the accounts/login route as an authenticated user I am redirected to the home page.</p>
</details>

<details>
  <summary>Sign up page</summary>
  <p>The sign up page is for an unauthenticated user to create an account. An authenticated user already has an account and so has no purpose for this page.</p>
  <p>I have confirmed that when I navigate to the accounts/signup route as an authenticated user I am redirected to the home page.</p>
</details>

#### Admin users only

<details>
  <summary>Admin site section</summary>
  <p>All routes under the /admin section should be accessible only to admin users.</p>
  <p>I have confirmed that when authenticated as a non-admin user I am required to authenticate as an admin user when accessing the /admin route.</p>
</details>
