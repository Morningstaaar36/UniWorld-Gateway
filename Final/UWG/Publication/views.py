from django.db import connection
from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
import base64


def publication_by_username(request, username):
    # Get the student ID using raw SQL query
    with connection.cursor() as cursor:
        cursor.execute("SELECT student_id FROM public.student WHERE name = %s", [username])
        row = cursor.fetchone()
        if row:
            student_id = row[0]
        else:
            return HttpResponse("Student not found.")

    # Get publications associated with the student using raw SQL query
    with connection.cursor() as cursor:
        cursor.execute("SELECT publication_id, title, publication_date, journal_name, pdf_blob FROM public.publication WHERE student_id = %s", [student_id])
        publications = cursor.fetchall()

    # Convert PDF blob to base64-encoded string
    modified_publications = []
    for publication in publications:
        modified_publication = list(publication)  # Convert tuple to list
        if modified_publication[4]:
            pdf_blob_base64 = base64.b64encode(modified_publication[4]).decode('utf-8')
            modified_publication[4] = pdf_blob_base64
        modified_publications.append(tuple(modified_publication))  # Convert list back to tuple

    # Check if publications exist
    has_publications = bool(modified_publications)

    # Construct a context dictionary with the publication information
    context = {
        'username': username,
        'publications': modified_publications,
        'has_publications': has_publications
    }

    # Pass the context to the HTML template
    return render(request, 'publicationHome.html', context)


# def updatePageRenderer(request, username):
#     return HttpResponse("Update publication page")


# def delete_publication(request, username):
#     return HttpResponse("Delete publication page")



# def addPageRenderer(request, username):
#     return HttpResponse("Add publication page")




def deletePublication(request, username):
    if request.method == 'GET':
        publication_id = request.GET.get('publication_id')
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM public.publication WHERE publication_id = %s", [publication_id])
            return redirect('publication_home_by_username', username=username)
        except Exception as e:
            return HttpResponse(f"Error deleting publication: {e}")
    else:
        return HttpResponse("Invalid method.")



def updatePublicationRenderer(request, username):
    if request.method == 'GET':
        publication_id = request.GET.get('publication_id')
        # Perform any necessary operations to render the update page
        context = {
            'username': username,
            'publication_id': publication_id
        }
        return render(request, 'updatePublication.html', context)
    else:
        return HttpResponse("Method not allowed.")
    
def addPublicationRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve user_id based on username
            cursor.execute("""
                SELECT user_id FROM public.user_table WHERE user_name = %s
            """, [username])
            user_id = cursor.fetchone()[0]  # Fetch the first result
            
            # Retrieve student_id associated with the user
            cursor.execute("""
                SELECT student_id FROM public.student WHERE user_id = %s
            """, [user_id])
            student_id = cursor.fetchone()[0]  # Fetch the first result
            
            # Pass username and student_id to the template
            return render(request, 'addPublicationRenderer.html', {'username': username, 'student_id': student_id})
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
    
    
    
def addPublication(request,username):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Retrieve form data from POST request
                student_id = request.POST.get('student_id')
                title = request.POST.get('title')
                publication_date = request.POST.get('publication_date')
                journal_name = request.POST.get('journal_name')
                pdf_blob = request.FILES.get('pdf_blob')
                
                # Check if all required fields are provided
                if student_id and title and publication_date:
                    # Insert publication data into the database
                    cursor.execute("""
                        INSERT INTO public.publication (student_id, title, publication_date, journal_name, pdf_blob)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [student_id, title, publication_date, journal_name, pdf_blob.read()])
                    
                    # Redirect to success page
                    return HttpResponse("Publication added successfully.")
                else:
                    return HttpResponse("Missing required fields.")
                
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")
    
    
    
def updaterPublication(request, username):
    if request.method == 'POST':
        # Retrieve publication_id from form data
        publication_id = request.POST.get('publication_id')

        # Initialize variables for form data
        title = request.POST.get('title', None)
        publication_date = request.POST.get('publication_date', None)
        journal_name = request.POST.get('journal_name', None)
        pdf_blob = request.FILES.get('pdf_blob', None)

        # Construct the SQL query
        sql = "UPDATE public.publication SET "
        update_values = []
        if title:
            sql += "title = %s, "
            update_values.append(title)
        if publication_date:
            sql += "publication_date = %s, "
            update_values.append(publication_date)
        if journal_name:
            sql += "journal_name = %s, "
            update_values.append(journal_name)
        if pdf_blob:
            sql += "pdf_blob = %s, "
            update_values.append(pdf_blob)

        # Check if any field was provided
        if not update_values:
            return HttpResponse("No fields provided for update.")

        # Remove the trailing comma and space from the SQL query
        sql = sql[:-2]

        # Add the WHERE clause for the publication_id
        sql += " WHERE publication_id = %s"
        update_values.append(publication_id)

        # Execute the SQL query with the provided parameters
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql, update_values)
                # Commit the transaction
                connection.commit()
                # Redirect to publication_by_username view
                return redirect('publication_home_by_username', username=username)
            except Exception as e:
                # Rollback the transaction in case of an error
                connection.rollback()
                return HttpResponse(f"Error updating publication: {str(e)}")
    else:
        return HttpResponse("Method not allowed.")