# Flight Management System (FMS)

A comprehensive web-based application for managing flight schedules, bookings, and passenger manifests. Built with **Django** and **Bootstrap 5**, this system provides distinct portals for Administrators and Passengers.

## 🚀 Features

### ✈️ For Passengers
* **User Authentication:** Secure registration and login system.
* **Dashboard:** Personalized dashboard showing upcoming flights.
* **Flight Search:** Search for flights by origin, destination, date, and cabin class.
* **Booking System:** Book flights for yourself and others.
* **Profile Management:** Update personal details, passport info, and change passwords.
* **My Bookings:** View a history of past and upcoming booked flights.

### 🛠️ For Administrators
* **Admin Dashboard:** High-level overview of total flights, bookings, and cancellations.
* **Flight Management:** * Add new flight schedules.
    * Edit existing flight details (delays, pricing changes).
    * Cancel or Delete flights.
* **Passenger Manifest:** View real-time passenger lists for any flight.
    * Search/Filter manifest by Name, Class, or Passport.
    * Remove passengers from a flight.
* **Reports & Analytics:**
    * View detailed operational reports (Revenue, Occupancy Rates).
    * **PDF Export:** Generate and download professional PDF reports (Financial, Occupancy, General).
    * *Note: Sensitive financial data is restricted to Superusers.*

## 📦 Prerequisites

* Python 3.10+
* pip (Python Package Manager)

## ⚙️ Installation Guide

1.  **Clone or Download the Repository**
    ```bash
    git clone <your-repo-url>
    cd FlightSystem
    ```

2.  **Create a Virtual Environment (Optional but Recommended)**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Database Migrations**
    Initialize the database tables.
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create a Superuser (Admin)**
    You need a superuser account to access the Admin Dashboard and Financial Reports.
    ```bash
    python manage.py createsuperuser
    ```
    *Follow the prompts to set a username, email, and password.*

6.  **Seed Initial Data (Optional)**
    If you have the seed script enabled, you can populate the database with dummy airports and flights:
    ```bash
    python manage.py seed_data
    ```

7.  **Run the Development Server**
    ```bash
    python manage.py runserver
    ```

    Access the application at: `http://127.0.0.1:8000/`

## 📖 Usage

### accessing the Admin Portal
1.  Log in using the **Superuser** account you created.
2.  You will be redirected to the **Admin Dashboard**.
3.  From here, you can add flights, view reports, or manage manifests.

### Accessing the Passenger Portal
1.  Click **Register** on the login page to create a new passenger account.
2.  Log in with your new credentials.
3.  You will be redirected to the **Passenger Dashboard** to search and book flights.

## 📄 Key Dependencies

* **Django 5.2.7**: The core web framework.
* **xhtml2pdf**: Used for generating downloadable PDF reports.
* **Bootstrap 5**: Frontend styling for a responsive and modern UI.
* **Bootstrap Icons**: For UI icons.
