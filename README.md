### Below is a summary that can serve as a README for the project, highlighting the API endpoints, setup, assumptions, and features:

## Setup Instructions

# Prerequisites: Python 3.8+, PostgreSQL.
# Installation:
1. Clone the repository
2. pip install -r requirements.txt  
3. Create DB and user
4. Run migrations and start
python manage.py migrate
python manage.py createsuperuser  # creates Admin
python manage.py runserver

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

3. Documentation:
    - GET /swagger/ – Swagger UI and OpenAPI docs for all endpoints (development use).
4. Bonus :
    - GET /api/availability/?start=<start_datetime>&end=<end_datetime> – Returns equipment availability within the given range. (Requires enabling the view as described in the code comments.)

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
🔄 Recurring bookings logic (loop with time delta)
📆 Equipment availability endpoint
📈 Foundation for reports: most-booked equipment, usage hours, etc.
🧪 Swagger-based interactive testing
