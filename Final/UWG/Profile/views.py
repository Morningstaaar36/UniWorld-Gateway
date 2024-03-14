from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection# Create your views here.
import base64


def index(request):
    return HttpResponse("Hello, world. You're at the Profile.")

def profile_by_username(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve student attributes by joining student and user_table
            cursor.execute("""
                SELECT s.student_id, s.name, s.email, s.cgpa, s.phone_number, s.image, s.date_of_birth
                FROM public.student s
                INNER JOIN public.user_table u ON s.user_id = u.user_id
                WHERE u.user_name = %s
            """, [username])
            student_data = cursor.fetchone()  # Fetch the first result
            
            if student_data:
                # Pass student attributes to the HTML template
                context = {
                    'username': username,
                    'student_id': student_data[0],
                    'name': student_data[1] if student_data[1] else 'Not given',
                    'email': student_data[2] if student_data[2] else 'Not given',
                    'cgpa': student_data[3] if student_data[3] else 'Not given',
                    'phone_number': student_data[4] if student_data[4] else 'Not given',
                    'image_data': base64.b64encode(student_data[5]).decode('utf-8') if student_data[5] else None,
                    'date_of_birth': student_data[6] if student_data[6] else 'Not given',
                }
                return render(request, 'profile.html', context)
            else:
                return HttpResponse("Student not found.")
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
def updateProfileRenderer(request, username):
    if request.method == 'POST':
        # Retrieve the student ID from the form data
        student_id = request.POST.get('student_id')
        if student_id:
            # Process the form data here
            # For example, you can perform database updates or other operations
            # Then render the template with the appropriate context
            return render(request, 'update_profile.html', {'username': username, 'student_id': student_id})
        else:
            return HttpResponse("Student ID not provided.")
    else:
        return HttpResponse("Invalid request method.")
    
    
    
    
def updateProfile(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the student ID from the form input
            student_id = request.POST.get('student_id')

            # Retrieve the updated fields from the form input
            updated_fields = {}

            # List of fields that can be updated
            allowed_fields = ['name', 'email', 'cgpa', 'phone_number', 'image']

            # Iterate through allowed fields and add to updated_fields if provided and selected for update
            for field in allowed_fields:
                update_field = f"update_{field}"
                if update_field in request.POST and request.POST.get(update_field) == "true":
                    if field == 'image' and field in request.FILES:
                        updated_fields[field] = request.FILES[field].read()
                    else:
                        updated_fields[field] = request.POST.get(field)

            # Construct the SQL query to update the student profile
            update_query = """
                UPDATE public.student
                SET {}
                WHERE student_id = %s
            """.format(', '.join([f"{field} = %s" for field in updated_fields]))

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, [v for k, v in updated_fields.items()] + [student_id])

            return HttpResponse("Student profile updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")