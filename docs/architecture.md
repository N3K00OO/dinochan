# Architecture overview

RagaSpace follows a modular Django architecture focused on clarity and maintainability.

## Modules

| Module | Responsibility |
| --- | --- |
| `venuebooking` | Global configuration, middleware, and settings management. |
| `venues` | Domain logic for venues, bookings, payments, reviews, and wishlists. |
| `templates/` | Tailwind-driven presentation with reusable partials. |
| `static/js/app.js` | Progressive enhancement via AJAX for wishlist and catalog filtering. |

## Security

- Secrets loaded from environment variables via `python-dotenv`.
- CSRF and session cookies support secure toggles for production.
- Password validators and Django's authentication middleware enforce robust user security.

## Data model

```text
Category ─┬─< Venue ─┬─< AddOn
          │         └─< VenueAvailability
          ├─< Booking ──── Payment (1:1)
          │          └─< Review
          └─< Wishlist
```

- `Booking` exposes helper methods for calculating invoice totals.
- `Payment` state transitions are encapsulated in views and signals.
- Signals ensure payment records stay synchronised with bookings and add-on changes.

## Request flow

1. **Auth** — Users authenticate via `/auth/login/` or create new accounts at `/auth/register/`.
2. **Discovery** — Landing and catalog pages provide filtering served by `VenueFilter` and AJAX endpoints.
3. **Wishlist** — Toggle endpoints (`WishlistToggleView` and `wishlist_toggle`) persist favourites.
4. **Booking** — `VenueDetailView` handles booking submissions and redirects to the payment step.
5. **Payment** — `BookingPaymentView` confirms the method and finalises invoices.
6. **Review** — Reviews are managed inline on the detail page with optimistic updates.

## Styling

- Tailwind CSS via CDN delivers the glassmorphism aesthetic.
- Background gradients and blurred panels emphasise a minimalist, modern interface.
- Components reuse consistent classes to ensure cohesive design.
