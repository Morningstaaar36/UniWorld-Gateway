from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.conf import settings
import psycopg2


def index(request):
    return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Get database connection parameters from settings.py
        dbname = settings.DATABASES['default']['NAME']
        user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']

        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=db_password,
                host=host,
                port=port
            )
            cur = conn.cursor()

            # Execute SQL query to insert user data
            cur.execute("INSERT INTO user_table (user_name, email, user_password) VALUES (%s, %s, %s)",
                        (name, email, password))

            # Commit the transaction
            conn.commit()

            # Retrieve the user_id for the inserted username
            cur.execute("SELECT user_id FROM user_table WHERE user_name = %s", (name,))
            row = cur.fetchone()
            if row:
                user_id = row[0]
            else:
                # Handle case where no user_id is found for the provided username
                return HttpResponse("Error: No user_id found for the provided username")

            # Insert data into student table
            cur.execute("INSERT INTO student (user_id, name, email) VALUES (%s, %s, %s)", (user_id, name, email))

            # Commit the transaction
            conn.commit()

            # Close cursor and connection
            cur.close()
            conn.close()

            # Redirect to Student/ with the username as a parameter
            return redirect('/Student/?username=' + name)

        except psycopg2.Error as e:
            return HttpResponse(f"Error occurred: {e}")

    return HttpResponse("Invalid request method.")


def signin(request):
    context = {}  # Initialize context dictionary
    if request.method == 'POST':
        # Handle signin form submission
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Connect to the database
        dbname = settings.DATABASES['default']['NAME']
        user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']

        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=db_password,
            host=host,
            port=port
        )

        cur = conn.cursor()

        # Query the database to fetch the stored password for the given username
        cur.execute("SELECT user_password FROM user_table WHERE user_name = %s", (username,))
        row = cur.fetchone()

        if row:
            stored_password = row[0]
            # Check if the provided password matches the stored password
            if password == stored_password:
                # Password matches, redirect to Student/ with the username as a parameter
                return redirect('/Student/?username=' + username)
            else:
                # Password doesn't match, add error message to context
                context['error'] = "Incorrect password. Please try again."
        else:
            # User with the provided username doesn't exist, add error message to context
            context['error'] = "User not found. Please check your username."

        # Close cursor and connection
        cur.close()
        conn.close()

    return HttpResponse("return to the previous page and try again.")
