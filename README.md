### Below is a summary that can serve as a README for the project, highlighting the API endpoints, setup, assumptions, and features:

## Setup Instructions

# Prerequisites: Python 3.8+, PostgreSQL.
# Installation:
1. Install Python packages: pip install django djangorestframework psycopg2-binary drf-yasg djangorestframework-simplejwt.
2. Set up PostgreSQL and create a database (e.g., equipment_booking) and user.
3. Configure the database settings in equipment_booking_project/settings.py.
4. Run python manage.py migrate to create tables.
5. Create a superuser for admin: python manage.py createsuperuser.
6. (Optional) Create groups "Manager" (and "Employee" if desired) in the admin, and assign users to those groups.
7. Run the server: python manage.py runserver.
   
- Postman/Curl: Use the provided endpoints (see below) to interact with the API. Authenticate with basic auth or obtain a JWT if configured.

## API Endpoints Documentation

(All endpoints are prefixed with /api/ as configured. All require authentication by default.)
1. Equipment:
    - GET /api/equipment/ – List Equipment. Returns a list of all equipment items with their details. Any logged-in user (Employee, Manager, Admin) can view. Supports query params like ?page= if pagination added (not implemented by default).
    - POST /api/equipment/ – Create Equipment. Admin only. Provide JSON with name, type, location (optional), total_quantity, is_available. Creates a new equipment entry.
    - GET /api/equipment/{id}/ – Retrieve Equipment. Any role can view details of a specific equipment item.
    - PUT /api/equipment/{id}/ – Full Update Equipment. Admin only. Replace all fields of an equipment item.
    - PATCH /api/equipment/{id}/ – Partial Update Equipment. Admin only. Update one or more fields.
    - DELETE /api/equipment/{id}/ – Delete Equipment. Admin only. Remove an equipment item (cascades to delete related bookings).
2. Bookings:
   - GET /api/bookings/ – List Bookings. Role-based output: Admin & Manager see all bookings; Employee sees only their own bookings.
    - POST /api/bookings/ – Create Booking. Employee (for self) or Manager (can specify a user) or Admin. JSON fields: equipment (id), start_time, end_time, quantity, and optionally user (if manager/admin creating for someone else). On success, returns the created booking. On failure (e.g., time conflict or overbooking), returns 400 with error message.
    - GET /api/bookings/{id}/ – Retrieve Booking. Allowed if the booking belongs to the user or the user is Manager/Admin.
    - PUT/PATCH /api/bookings/{id}/ – Update Booking. (Not heavily tested in our implementation. By default, it would allow changing times or quantity. We recommend caution or extending validation to handle updates similar to creation to avoid introducing conflicts.)
    - DELETE /api/bookings/{id}/ – Cancel Booking. Allowed if Admin/Manager or the booking's owner. Employees can delete (cancel) only their own bookings. This will permanently delete the booking record in our setup. (Optionally, one could mark it as canceled instead.)
3. Auth:
   - POST /api/token/ – (If JWT enabled) Obtain JWT token pair. Supply JSON {"username": "user", "password": "pass"}.
   - POST /api/token/refresh/ – Refresh JWT token.
    Django's session auth login can be done via the admin site or browsable API login form.
4. Documentation:
    - GET /swagger/ – Swagger UI and OpenAPI docs for all endpoints (development use).
5. Bonus (if enabled):
    - GET /api/availability/?start=<start_datetime>&end=<end_datetime> – Returns equipment availability within the given range. (Requires enabling the view as described in the code comments.)
    - Recurring booking fields (recurrence_interval, recurrence_count) in booking creation can be enabled to allow creating multiple bookings in one request.

## Assumptions & Notes

1. User Roles:
   - We assume Admin users will be created as Django superusers or staff. They have full access.
   - Manager and Employee are distinguished by group membership. If a user is in the "Manager" group (and not staff), we    treat them as Manager. All other non-staff users are Employees. This was a design choice to avoid a custom user model. In a real system, you might use a more explicit field or a separate Profile model.
2. Managers' Permissions: Managers can create bookings on behalf of any employee and can view all bookings. We assume managers can also cancel any booking (since they might manage schedules). If you want to restrict managers to only manage their subordinates, you'd need to introduce a concept of "manager's team" (not implemented here).
3. Employees' Permissions: Employees can only create bookings for themselves and only see/cancel their own.
4. Equipment Availability: The system prevents double-booking beyond available quantity for overlapping times by checking existing bookings in the requested interval. This is done at booking creation (and should also be done if updating a booking's time). There is a slight risk of race conditions if two bookings are made at the same time for the last item – in a real app, database-level locking or transactions should be considered. For this tutorial, it's simplified.
5. Time slots and Format: We use ISO 8601 format for datetimes (the default for DRF serializers). All times are assumed to be in UTC (or the Django project’s time zone). Make sure to provide timezone info (e.g., "Z" for UTC) in the timestamps. The system does not currently send notifications or suggest alternative slots on conflicts (that was mentioned as a nice-to-have in requirements but is not implemented).
6. Cancel vs Delete: We chose to implement cancellation by deletion. In production, you'd likely keep the booking and mark it canceled instead, especially to produce reports (like "most booked equipment" might exclude canceled bookings or count them differently). We kept a status field in anticipation of that, but didn't fully utilize it beyond preventing overlapping calculations from considering canceled bookings.
7. Admin Panel: We provided basic admin registrations. This allows easy creation of Equipment and Bookings for testing. In a production API-only service, you might not use the admin at all.
8. Swagger: The included Swagger (drf-yasg) is a great way to visualize and test the API. If deploying publicly, ensure to restrict access or remove it if not needed. The schema info defined includes just a basic title and description. One can expand it with per-endpoint descriptions by using DRF view/serializer docstrings or drf_yasg annotations.
   
- Feature Summary
1. Equipment Management: Admins can add/edit/remove equipment, including setting a piece as unavailable. All users can list and view equipment details. The system stores equipment name, type, location, quantity.
2. Booking Management: Employees and Managers can create bookings (with appropriate restrictions). The system ensures no overlapping bookings exceed equipment availability. Users can view bookings (scope depends on role) and cancel bookings. The model tracks who made each booking and its status.
3. Authentication & Roles: Uses Django's auth system. Ready for JWT if needed. Role-based permission logic is implemented for endpoints.
4. API Documentation: Interactive docs via Swagger UI.

- Bonus Features
1. Recurring Bookings: Code structure is prepared to handle recurring bookings in the future. With minor modifications (adding fields and logic as commented in code), the system can create multiple bookings in one go for a recurring event.
2. Advanced Availability: We sketched an endpoint to query availability of equipment for a given time range. This can help users pick an open slot or see how many items are free. Further enhancements could include a calendar view or a report of availability per day/week which would build on this logic.
3. Reporting: While not implemented, the data model supports deriving reports like "most booked equipment" (simply count bookings per equipment) or "usage stats per type" (e.g., total hours booked per equipment type). These could be added as additional endpoints or admin reports.
