# Property Dealer API (FastAPI + JWT)

Matches your notebook plan: Property Dealer platform, mobile-number + OTP login, category Rent/Sale, property details.

## Run it

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Docs at `http://127.0.0.1:8000/docs`.

## Auth flow (mobile number + OTP -> JWT)

1. `POST /auth/request-otp` `{ "phone_number": "9876543210" }`
   Returns `debug_otp` for testing — wire this to a real SMS provider (Twilio, MSG91, etc.) before going live.
2. `POST /auth/verify-otp` `{ "phone_number": "9876543210", "code": "1234", "name": "Ramesh" }`
   Creates the user on first login, returns `{ "access_token": ..., "token_type": "bearer" }`.
3. Use the token as `Authorization: Bearer <token>` on protected routes.
4. `GET /auth/me` returns the logged-in user.

## Property endpoints

- `POST /properties` (auth required) — create a listing
- `GET /properties?category=Rent` (public) — browse listings
- `GET /properties/{id}` (public)
- `PUT /properties/{id}` (auth, owner only)
- `DELETE /properties/{id}` (auth, owner only)

Fields follow your notes: `property_image` (multiple, stored as a list), `property_name`, `property_slug`,
`property_address`, `property_floor` (G/F/S), `property_price`, `property_washroom` (Y/N), `property_type`,
`category` (Rent/Sale), `personal_name`, `personal_phone`, `status`.

## Notes / assumptions I made

- **OTP delivery**: not wired to an SMS provider — `debug_otp` is returned directly in the response so you
  can test the flow. Swap in Twilio/MSG91 etc. in `auth_router.request_otp`.
- **property_floor / property_type**: your notes list options "G F S" and "Y N / R S" next to these fields
  without labels, so I guessed Ground/First/Second for floor and left `property_type` as free text —
  tell me what those option sets actually mean and I'll lock down the enums.
- **SECRET_KEY**: currently a placeholder in `app/config.py` — replace with a real secret (env var) before deploying.
- **Database**: SQLite by default for easy local testing; change `DATABASE_URL` in `app/config.py` for Postgres/MySQL in production.
