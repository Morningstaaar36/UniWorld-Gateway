import os
from django.shortcuts import render
from django.http import HttpResponse
import psycopg2
from django.conf import settings
# Create your views here.
import base64




def documents_home_by_username(request, username):
    # return HttpResponse(f"docuements for {username}")
    return render(request, 'documentHomePage.html', {'username': username})



def add_document(request, username):

        # return HttpResponse(f"Add a document{username}")
        return render(request, 'add_docuement_page.html', {'username': username})


def see_documents(request, username):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

        # Create a cursor
        cur = conn.cursor()

        # Execute the query to retrieve the student ID based on the username
        cur.execute("""
            SELECT student_id FROM student WHERE name = %s
        """, (username,))
        student_row = cur.fetchone()

        if student_row:
            student_id = student_row[0]

            # Execute the query to retrieve document information for the given student ID
            cur.execute("""
                SELECT document_type, pdf_link, upload_date
                FROM document 
                WHERE student_id = %s
            """, (student_id,))
            
            # Fetch all rows
            document_info = cur.fetchall()

            # Process PDF content
            pdf_data = []
            for document in document_info:
                with open(document[1], 'rb') as f:
                    pdf_content = f.read()
                    pdf_data.append(base64.b64encode(pdf_content).decode())

            # Close cursor and connection
            cur.close()
            conn.close()

            # Pass the document information and PDF content to the template for rendering
            return render(request, 'see_documents_page.html', {'documents': zip(document_info, pdf_data), 'username': username})
        else:
            return HttpResponse("Student not found")

    except psycopg2.Error as e:
        # Handle any database errors
        return HttpResponse(f"Database error: {e}")

    except Exception as e:
        # Handle any other errors
        return HttpResponse(f"Error: {e}")



def manage_documents(request, username):
    return HttpResponse(f"Manage documents{username}")


def add_document_analyze(request, username):
    if request.method == 'POST':
        # Retrieve form data
        document_type = request.POST.get('type')
        pdf_file = request.FILES.get('pdf')

        # Database connection parameters
        dbname = settings.DATABASES['default']['NAME']
        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']
        conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )

            # Cursor
        cur = conn.cursor()
        try:
            # Connect to the PostgreSQL database


            # Save the uploaded PDF file to a specific directory
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', pdf_file.name)
            with open(file_path, 'wb') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)

            # Execute SQL to retrieve student_id based on username
            cur.execute("""
                SELECT student_id FROM student WHERE name = %s
            """, (username,))
            row = cur.fetchone()

            if row:
                student_id = row[0]
                # Execute SQL to insert document into the database
                cur.execute("""
                    INSERT INTO document (student_id, document_type, pdf_link) 
                    VALUES (%s, %s, %s)
                """, (student_id, document_type, file_path))
                # Commit changes to the database
                conn.commit()
                return HttpResponse("Document added successfully!")  # Redirect or render success message
            else:
                return HttpResponse("Student not found!")  # Username not found

        except psycopg2.Error as e:
            print("Error:", e)
            return HttpResponse("An error occurred while adding the document.")

        finally:
            # Close cursor and connection
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    # If the request method is not POST, render a default response
    return HttpResponse("This is the add_document_analyze view. Make a POST request to add a document.")


def see_documents_analyze(request,username):
    return HttpResponse(f"fuck you")


def manage_documents_analyze(request,username):
    return HttpResponse(f"fuck you")