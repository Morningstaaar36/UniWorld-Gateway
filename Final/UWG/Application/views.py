from django.db import connection
# from django.forms import DateField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from datetime import datetime 

# Create your views here.
# Application/views.py
from django.shortcuts import render
from django.urls import reverse

import psycopg2
from django.http import HttpResponse
from django.template import loader
from django.db import connection
from django.db import connection
from django.http import HttpResponse
from django.template import loader
import psycopg2
import base64

operationDictionaries = {
    'add': {
        'toefl': 'addTOEFLRenderer',
        'gre_score': 'addGRERenderer',
        'ielts_score': 'addIELTSRenderer',
        'gmat_score': 'addGMATRenderer',
        'contact_info': 'addContactInfoRenderer',
        'citizenship_info': 'addCitizenshipInfoRenderer',
        'academic_record': 'addAcademicRecordRenderer',
        'portfolio': 'addPortfolioRenderer',
        'biological_info': 'addBiologicalInfoRenderer',
        'personal_info': 'addPersonalInfoRenderer',
        'address': 'addAddressRenderer',
        'program': 'addProgramSelectionRenderer',
        'submit':'submitRenderer',
        'fSubmit':'finalSubmit',
        'lastShow':'lastShowRenderer'
    },
    'update': {
        'toefl': 'updateTOEFLRenderer',
        'gre_score': 'updateGRERenderer',
        'ielts_score': 'updateIELTSRenderer',
        'gmat_score': 'updateGMATRenderer',
        'contact_info': 'updateContactInfoRenderer',
        'citizenship_info': 'updateCitizenshipInfoRenderer',
        'academic_record': 'updateAcademicRecordRenderer',
        'portfolio': 'updatePortfolioRenderer',
        'biological_info': 'updateBiologicalInfoRenderer',
        'personal_info': 'updatePersonalInfoRenderer',
        'address': 'updateAddressRenderer',
    },
    'see': {
        'toefl': 'seeTOEFL',
        'gre_score': 'seeGRE',
        'ielts_score': 'seeIELTS',
        'gmat_score': 'seeGMAT',
        'contact_info': 'seeContactInfo',
        'citizenship_info': 'seeCitizenshipInfo',
        'academic_record': 'seeAcademicRecord',
        'portfolio': 'seePortfolio',
        'biological_info': 'seeBiologicalInfo',
        'personal_info': 'seePersonalInfo',
        'address': 'seeAddress',
    },
    'delete': {
        'toefl': 'deleteTOEFL',
        'gre_score': 'deleteGRE',
        'ielts_score': 'deleteIELTS',
        'gmat_score': 'deleteGMAT',
        'contact_info': 'deleteContactInfo',
        'citizenship_info': 'deleteCitizenshipInfo',
        'academic_record': 'deleteAcademicRecord',
        'portfolio': 'deletePortfolio',
        'biological_info': 'deleteBiologicalInfo',
        'personal_info': 'deletePersonalInfo',
        'address': 'deleteAddress',
    },
    'next': {
        'personal_info': 'biological_info',
        'biological_info': 'contact_info',
        'contact_info': 'address',
        'address': 'citizenship_info',
        'citizenship_info': 'academic_record',
        'academic_record': 'portfolio',
        'portfolio': 'gmat_score',
        'gmat_score': 'gre_score',
        'gre_score': 'ielts_score',
        'ielts_score': 'toefl',
        'toefl': 'program',
        'program' : 'submit',
        'submit': 'fSubmit',
        'fSubmit': 'lastShow'
    }
}
def check_valid_application(username):
    try:
        # Get the application ID using the get_application_id function
        with connection.cursor() as cursor:
            get_app_id_query = """
                SELECT public.get_application_id(%s)
            """
            cursor.execute(get_app_id_query, [username])
            application_id = cursor.fetchone()[0]

            # Check if the application ID is not None
            if application_id:
                # Execute the SQL query to check valid application
                sql_query = """
                    SELECT table_name, output_string 
                    FROM public.valid_application(%s)
                """
                cursor.execute(sql_query, [application_id])
                result = cursor.fetchall()
                
                # Check if the query returned any rows
                return not bool(result)
            else:
                # If no application ID found, return False
                return False
    except Exception as e:
        print(f"Error checking valid application: {e}")
        return False
def applicationHomeRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Find the student_id from the student table using raw SQL
            query_student_id = "SELECT student_id FROM public.student WHERE name = %s"
            cursor.execute(query_student_id, (username,))
            student_id = cursor.fetchone()
            if check_valid_application(username=username): 
                return HttpResponse("good job")
            if student_id:
                student_id = student_id[0]  # Extract the student_id from the result tuple

                # Check if there is any application_id for that student
                query_check_application = """
                    SELECT application_id 
                    FROM public.application_form 
                    WHERE student_id = %s
                """
                cursor.execute(query_check_application, (student_id,))
                application_id = cursor.fetchone()

                if not application_id:
                    # If no application exists, insert a new record into the application_form table
                    query_insert_application = """
                        INSERT INTO public.application_form (application_date, last_save_date, student_id, last_filled_table)
                        VALUES (current_date, current_date, %s, NULL)
                    """
                    cursor.execute(query_insert_application, (student_id,))
                    connection.commit()

                    # Pass the data to the HTML template
                    template = loader.get_template('applicationHome.html')
                    context = {
                        'username': username,
                        'has_application_id': False,
                        'has_personal_info': False,
                        'has_biological_info': False,
                        'has_contact_info': False,
                        'has_address_info': False,
                        'has_citizenship_info': False,
                        'has_academic_record': False,
                        'has_portfolio': False,  # Initialize as False when no application exists
                        'has_gmat_score': False,  # Initialize as False when no GMAT record exists
                        'has_gre_score': False,   # Initialize as False when no GRE record exists
                        'has_ielts_score': False,  # Initialize as False when no IELTS record exists
                        'has_toefl_score': False   # Initialize as False when no TOEFL record exists
                    }
                    return HttpResponse(template.render(context, request))
                else:
                    application_id = application_id[0]

                    # Check if there is a record in portfolio for the application_id
                    query_portfolio_id = """
                        SELECT portfolio_no 
                        FROM public.portfolio 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_portfolio_id, (application_id,))
                    portfolio_id = cursor.fetchone()
                    has_portfolio = bool(portfolio_id)

                    # Check if there is a record in academic_record for the application_id
                    query_academic_record_id = """
                        SELECT record_id 
                        FROM public.academic_record 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_academic_record_id, (application_id,))
                    academic_record_id = cursor.fetchone()
                    has_academic_record = bool(academic_record_id)

                    # Check if there is a record in personal_info for the application_id
                    query_personal_info_id = """
                        SELECT personal_info_id 
                        FROM public.personal_info 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_personal_info_id, (application_id,))
                    personal_info_id = cursor.fetchone()
                    has_personal_info = bool(personal_info_id)

                    # Check if there is a record in biological_info for the application_id
                    query_biological_info_id = """
                        SELECT bio_info_id 
                        FROM public.biological_info 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_biological_info_id, (application_id,))
                    biological_info_id = cursor.fetchone()
                    has_biological_info = bool(biological_info_id)

                    # Check if there is a record in contact_info for the application_id
                    query_contact_info_id = """
                        SELECT contact_id 
                        FROM public.contact_info 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_contact_info_id, (application_id,))
                    contact_info_id = cursor.fetchone()
                    has_contact_info = bool(contact_info_id)

                    # Check if there is a record in address for the application_id
                    query_address_id = """
                        SELECT address_id 
                        FROM public.address 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_address_id, (application_id,))
                    address_id = cursor.fetchone()
                    has_address_info = bool(address_id)

                    # Check if there is a record in citizenship_info for the application_id
                    query_citizenship_info_id = """
                        SELECT citizenship_id 
                        FROM public.citizenship_info 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_citizenship_info_id, (application_id,))
                    citizenship_info_id = cursor.fetchone()
                    has_citizenship_info = bool(citizenship_info_id)

                    # Check if there is a record in gmat_score for the application_id
                    query_gmat_score_id = """
                        SELECT gmat_id 
                        FROM public.gmat_score 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_gmat_score_id, (application_id,))
                    gmat_score_id = cursor.fetchone()
                    has_gmat_score = bool(gmat_score_id)

                    # Check if there is a record in gre_score for the application_id
                    query_gre_score_id = """
                        SELECT gre_id 
                        FROM public.gre_score 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_gre_score_id, (application_id,))
                    gre_score_id = cursor.fetchone()
                    has_gre_score = bool(gre_score_id)

                    # Check if there is a record in ielts_score for the application_id
                    query_ielts_score_id = """
                        SELECT ielts_id 
                        FROM public.ielts_score 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_ielts_score_id, (application_id,))
                    ielts_score_id = cursor.fetchone()
                    has_ielts_score = bool(ielts_score_id)

                    # Check if there is a record in toefl for the application_id
                    query_toefl_score_id = """
                        SELECT toefl_id 
                        FROM public.toefl 
                        WHERE application_id = %s
                    """
                    cursor.execute(query_toefl_score_id, (application_id,))
                    toefl_score_id = cursor.fetchone()
                    has_toefl_score = bool(toefl_score_id)

                    # Pass the data to the HTML template
                    template = loader.get_template('applicationHome.html')
                    context = {
                        'username': username,
                        'has_application_id': True,
                        'has_personal_info': has_personal_info,
                        'has_biological_info': has_biological_info,
                        'has_contact_info': has_contact_info,
                        'has_address_info': has_address_info,
                        'has_citizenship_info': has_citizenship_info,
                        'has_academic_record': has_academic_record,
                        'has_portfolio': has_portfolio,  # Update based on the presence of portfolio records
                        'has_gmat_score': has_gmat_score,  # Update based on the presence of GMAT records
                        'has_gre_score': has_gre_score,    # Update based on the presence of GRE records
                        'has_ielts_score': has_ielts_score,  # Update based on the presence of IELTS records
                        'has_toefl_score': has_toefl_score   # Update based on the presence of TOEFL records
                    }
                    return HttpResponse(template.render(context, request))
            else:
                return HttpResponse("Student not found.")

    except Exception as error:
        return HttpResponse(f"Error: {error}")



def createApplication(request, username):
    return redirect('addPersonalInfoRenderer', username=username) 
   

def resumeApplication(request, username):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT student.student_id, application_form.application_id, application_form.last_filled_table
                FROM user_table
                INNER JOIN student ON user_table.user_id = student.user_id
                INNER JOIN application_form ON student.student_id = application_form.student_id
                WHERE user_table.user_name = %s
                ORDER BY application_form.application_date DESC
                LIMIT 1
                """,
                [username]
            )
            row = cursor.fetchone()
            if row:
                student_id, application_id, last_filled_table = row
                next_table = operationDictionaries['next'].get(last_filled_table)
                if next_table:
                    next_url = reverse(operationDictionaries['add'][next_table], kwargs={'username': username})
                    return redirect(next_url)
                else:
                    return HttpResponse("Next table not found.")
            else:
                return HttpResponse("No data found for the provided username.")
    except Exception as e:
        # Handle any database errors
        return HttpResponse(f"Error: {str(e)}")
    
    
def deleteApplication(request):
    return HttpResponse("This is the delete application view.")

def stopApplication(request):
    return HttpResponse("This is the stop application view.")

def submitRenderer(request, username):
    # Construct SQL query to retrieve validation results
    print('*************************************************************************')
    sql_query = """
        SELECT table_name, output_string 
        FROM public.valid_application(%s)
    """

    # Call the PL/pgSQL function to get the application ID
    get_application_id_query = """
        SELECT public.get_application_id(%s)
    """

    # List to store table names with non-empty output strings
    non_empty_tables = []

    # Dictionary to store the data
    validation_data = {
        'personal_info': {'addLink': 'addPersonalInfoRenderer', 'updateLink': 'updatePersonalInfoRenderer', 'value': ''},
        'academic_record': {'addLink': 'addAcademicRecordRenderer', 'updateLink': 'updateAcademicRecordRenderer', 'value': []},
        'portfolio': {'addLink': 'addPortfolioRenderer', 'updateLink': 'updatePortfolioRenderer', 'value': ''},
        'address': {'addLink': 'addAddressRenderer', 'updateLink': 'updateAddressRenderer', 'value': ''},
        'biological_info': {'addLink': 'addBiologicalInfoRenderer', 'updateLink': 'updateBiologicalInfoRenderer', 'value': ''},
        'ielts_score': {'addLink': 'addIELTSRenderer', 'updateLink': 'updateIELTSRenderer', 'value': ''},
        'toefl': {'addLink': 'addTOEFLRenderer', 'updateLink': 'updateTOEFLRenderer', 'value': ''},
        'gre_score': {'addLink': 'addGRERenderer', 'updateLink': 'updateGRERenderer', 'value': ''},
        'gmat_score': {'addLink': 'addGMATRenderer', 'updateLink': 'updateGMATRenderer', 'value': ''},
        'contact_info': {'addLink': 'addContactInfoRenderer', 'updateLink': 'updateContactInfoRenderer', 'value': ''},
        'citizenship_info': {'addLink': 'addCitizenshipInfoRenderer', 'updateLink': 'updateCitizenshipInfoRenderer', 'value': ''},
    }

    # Execute the query to get the application ID
    with connection.cursor() as cursor:
        cursor.execute(get_application_id_query, [username])
        application_id = cursor.fetchone()[0]  # Fetch the application ID

        # Execute the SQL query with the retrieved application ID
        cursor.execute(sql_query, [application_id])
        validation_results = cursor.fetchall()

    # Populate the dictionary with data
    for row in validation_results:
        table_name = row[0]
        output_string = row[1]

        if output_string != '':
            non_empty_tables.append(table_name)  # Add table name to the list

        # For academic_record, append the output_string to the array
        if table_name == 'academic_record':
            # Check if the output_string contains a colon (':')
            if ':' in output_string:
                # Extract record ID and its corresponding string
                record_id, record_string = output_string.split(': ')
                record_dict = {'record_id': record_id, 'record_string': record_string}
                validation_data[table_name]['value'].append(record_dict)
            else:
                # If the output_string doesn't contain a colon, set record_id to an empty string
                record_id = ''
                record_dict = {'record_id': record_id, 'record_string': output_string}
                validation_data[table_name]['value'].append(record_dict)
        else:
            # For other tables, store the output_string directly
            if table_name == 'toefl_score':
                table_name = 'toefl'
            validation_data[table_name]['value'] = output_string

    # Remove keys and values from validation_data for tables not present in non_empty_tables
    for key in list(validation_data.keys()):
        if key not in non_empty_tables:
            del validation_data[key]
            
    can_submit = not bool(validation_results)
    print(can_submit)
    # Return a simple message along with can_submit variable
    return render(request, 'submit_renderer.html', {'username': username, 'validation_data': validation_data, 'can_submit': can_submit})

def finalSubmit(request, username):
    # Check if the request method is POST

        # Execute raw SQL to update the last_filled_table column
    update_query = """
        UPDATE public.application_form AS af
        SET last_filled_table = 'submit'
        FROM public.student AS s
        JOIN public.user_table AS ut ON s.user_id = ut.user_id
        WHERE af.student_id = s.student_id
        AND ut.user_name = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(update_query, [username])
    return HttpResponse("Successfully updated last_filled_table")
 
    
       
def lastShowRenderer(request, username):
    context = {
        'username': username,
        'last_show': 'last show'
    }
    return render(request, 'lastShow.html', context)

def addProgramSelectionRenderer(request, username):
    # Initialize variables to store fetched data
    locations = []
    universities = []
    programs = []
    departments = []

    with connection.cursor() as cursor:
        # Fetch location names
        cursor.execute("SELECT DISTINCT location FROM public.university")
        locations_result = cursor.fetchall()
        locations = [row[0] for row in locations_result]

        # Fetch university names
        cursor.execute("SELECT DISTINCT name FROM public.university")
        universities_result = cursor.fetchall()
        universities = [row[0] for row in universities_result]

        # Fetch program names
        cursor.execute("SELECT DISTINCT programme_name FROM public.programme")
        programs_result = cursor.fetchall()
        programs = [row[0] for row in programs_result]

        # Fetch department names
        cursor.execute("SELECT DISTINCT department_name FROM public.department")
        departments_result = cursor.fetchall()
        departments = [row[0] for row in departments_result]

    # Constructing context to pass to the template
    context = {
        'username': username,
        'locations': locations,
        'universities': universities,
        'programs': programs,
        'departments': departments,
    }

    # Pass the context to the template and render it
    return render(request, 'addProgrammeHome.html', context)




def addProgramSelectionByLocationRenderer(request, username):
    if request.method == 'POST':
        location = request.POST.get('location')
        try:
            # Retrieve programs based on the selected location
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM public.get_programs_by_university_location(%s)", [location])
                programs = cursor.fetchall()
            # Render the HTML template with the fetched programs and username
            return render(request, 'showProgrammesSelectLocation.html', {'username': username, 'programs': programs})
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return HttpResponse(error_message, status=500)
    else:
        return HttpResponse("Invalid request method")







def addProgramSelectionByCriteriaRenderer(request, username):
    if request.method == 'POST':
        # Retrieve data from form checkboxes and select boxes
        department = request.POST.get('department') if request.POST.get('departmentCheckbox') else None
        program = request.POST.get('program') if request.POST.get('programCheckbox') else None
        university = request.POST.get('university') if request.POST.get('universityCheckbox') else None

        try:
            # Retrieve programs based on the selected criteria
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM public.get_programs_by_criteria(%s, %s, %s)", [department, university, program])
                programs = cursor.fetchall()
            
            # Render the HTML template with the fetched programs and username
            return render(request, 'showProgrammesSelectLocation.html', {'username': username, 'programs': programs})
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return HttpResponse(error_message, status=500)
    else:
        return HttpResponse("Invalid request method")   
    
    
def addProgramSelection(request, username):
    if request.method == 'POST':
        # Retrieve selected program IDs from the form data
        selected_programs_str = request.POST.get('selected_programs')
        selected_programs = [int(program_id) for program_id in selected_programs_str.split(',')]
        username_input = username

        try:
            # Retrieve application ID for the given username using raw SQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT public.get_application_id(%s)", [username_input])
                application_id = cursor.fetchone()[0]

            # Insert the selected program IDs along with the application ID into the database
            with connection.cursor() as cursor:
                for program_id in selected_programs:
                    cursor.execute("INSERT INTO public.program_application (program_id, application_id) VALUES (%s, %s)", [program_id, application_id])

            return HttpResponse("Program selection submitted successfully.")
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
    else:
        return HttpResponse("Invalid request method.")
    
        
def seeProgramSelection(request, username):
    try:
        # Execute the PostgreSQL function to get the application ID for the username
        with connection.cursor() as cursor:
            cursor.execute("SELECT get_application_id(%s)", [username])
            application_id = cursor.fetchone()[0]  # Fetch the application ID from the result

            # Check if an application ID was retrieved
            if application_id is not None:
                # Query to fetch program selection details
                query = """
                    SELECT 
                        pa.program_application_id,
                        u.university_name,
                        u.university_location,
                        u.university_established_date,
                        u.university_rank,
                        u.university_max_student,
                        d.department_name,
                        d.department_head,
                        d.department_established_date,
                        d.department_max_student,
                        p.programme_name,
                        p.tuition_fee,
                        p.duration,
                        p.application_deadline,
                        p.programme_ranking,
                        p.programme_max_student
                    FROM 
                        (
                            SELECT 
                                university_id,
                                name AS university_name,
                                location AS university_location,
                                established_date AS university_established_date,
                                rank AS university_rank,
                                university_max_student
                            FROM 
                                public.university
                        ) AS u
                    JOIN 
                        (
                            SELECT 
                                department_id,
                                university_id,
                                department_name,
                                department_head,
                                established_date AS department_established_date,
                                department_max_student
                            FROM 
                                public.department
                        ) AS d ON u.university_id = d.university_id
                    JOIN 
                        (
                            SELECT 
                                programme_id,
                                department_id,
                                programme_name,
                                tuition_fee,
                                duration,
                                application_deadline,
                                programme_ranking,
                                programme_max_student
                            FROM 
                                public.programme
                        ) AS p ON d.department_id = p.department_id
                    JOIN 
                        public.program_application pa ON p.programme_id = pa.program_id
                    WHERE 
                        pa.application_id = %s
                """

                # Execute the query with application ID
                cursor.execute(query, [application_id])

                # Fetch all rows
                rows = cursor.fetchall()

                # Initialize an empty list to store program selections
                program_selections = []

                # Iterate over each row and construct a dictionary for each program selection
                for row in rows:
                    program_selection_dict = {
                        'program_application_id': row[0],
                        'username': username,
                        'university_name': row[1],
                        'university_location': row[2],
                        'university_established_date': row[3],
                        'university_rank': row[4],
                        'university_max_student': row[5],
                        'department_name': row[6],
                        'department_head': row[7],
                        'department_established_date': row[8],
                        'department_max_student': row[9],
                        'programme_name': row[10],
                        'tuition_fee': row[11],
                        'duration': row[12],
                        'application_deadline': row[13],
                        'programme_ranking': row[14],
                        'programme_max_student': row[15]
                    }
                    # Append the dictionary to the list
                    program_selections.append(program_selection_dict)

                # Render HTML template with program selections and username as context data
                return render(request, 'programSelectionPage.html', {'program_selections': program_selections, 'username': username})

            else:
                return HttpResponse(f"No program selection found for {username}")

    except Exception as e:
        # Handle exceptions
        return HttpResponse(f"Error: {str(e)}")
    
    
def deleteProgramSelection(request, username):
    if request.method == 'GET':
        program_application_id = request.GET.get('program_application_id')
        if program_application_id:
            try:
                # Execute SQL DELETE statement to remove the program application record
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM public.program_application WHERE program_application_id = %s", [program_application_id])
                
                # Redirect to the seeProgramSelection view after successful deletion
                return redirect('seeProgramSelection', username=username)
            except Exception as e:
                return HttpResponse(f"Error occurred during deletion: {str(e)}")
        else:
            return HttpResponse("No program application ID provided for deletion.")
    else:
        return HttpResponse("Invalid request method for deleting program selection.")






def submitSelection(request, username):
    # Construct the SQL query to call the PL/pgSQL function and retrieve the application ID
    sql_query = "SELECT public.get_application_id(%s)"

    # Execute the SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query, [username])
        application_id = cursor.fetchone()[0]  # Fetch the result of the function call

    # Construct another SQL query to update the last_filled_table to 'program'
    update_query = "UPDATE public.application_form SET last_filled_table = 'program' WHERE application_id = %s"

    # Execute the update query
    with connection.cursor() as cursor:
        cursor.execute(update_query, [application_id])

    # Return a confirmation response
    return HttpResponse("Submission successful. Last filled table updated to 'program'.")


# for personal info






def addPersonalInfoRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using raw SQL query
            query_application_id = f"""
                SELECT af.application_id 
                FROM public.user_table u
                INNER JOIN public.student s ON u.user_id = s.user_id
                INNER JOIN public.application_form af ON s.student_id = af.student_id
                WHERE u.user_name = '{username}'
                AND af.application_id IS NOT NULL
                LIMIT 1
            """
            cursor.execute(query_application_id)
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdatePersonalInfo.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")


        
def addPersonalInfo(request, username):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Retrieve the application_id from the POST data
                application_id = request.POST.get('application_id')
                name = request.POST.get('name')
                full_name = request.POST.get('full_name')
                legal_name = request.POST.get('legal_name')
                maiden_name = request.POST.get('maiden_name')
                image = request.FILES.get('image')  # Retrieve the image file

                # Check if all required fields are provided
                if name and full_name and legal_name and maiden_name and application_id:
                    # Insert into personal_info table
                    cursor.execute("""
                        INSERT INTO public.personal_info (name, full_name, legal_name, maiden_name, application_id, image)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, [name, full_name, legal_name, maiden_name, application_id, image.read()])
                    
                    # Update last_filled_table to 'personal_info'
                    cursor.execute("""
                        UPDATE public.application_form
                        SET last_filled_table = 'personal_info'
                        WHERE student_id = (
                            SELECT s.student_id
                            FROM public.student s
                            INNER JOIN public.user_table u ON s.user_id = u.user_id
                            WHERE u.user_name = %s
                        )
                    """, [username])
                    
                    # Redirect to addBiologicalInfoRenderer and pass username
                    return redirect('addBiologicalInfoRenderer', username=username)
                else:
                    return HttpResponse("Missing required fields.")
                
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")
    

def seePersonalInfo(request, username):
    try:
        # Retrieve personal information for the given username
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name, full_name, legal_name, maiden_name, image
                FROM public.personal_info
                WHERE application_id = (
                    SELECT public.get_application_id(%s)
                )
            """, [username])
            personal_info = cursor.fetchone()

        # Check if personal information exists
        if personal_info:
            # Extract image data
            image_data = personal_info[4]

            # Convert binary image data to base64 for embedding in HTML
            if image_data:
                image_data_base64 = base64.b64encode(image_data).decode('utf-8')
            else:
                image_data_base64 = None

            # Pass the retrieved personal information and image data to the HTML template
            context = {
                'username': username,
                'name': personal_info[0],
                'full_name': personal_info[1],
                'legal_name': personal_info[2],
                'maiden_name': personal_info[3],
                'image_data': image_data_base64
            }
            return render(request, 'seePersonalInfo.html', context)
        else:
            return HttpResponse(f"No personal information found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")




def deletePersonalInfo(request, username):
    try:
        # Retrieve the application ID for the given username
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()
            application_id = row[0] if row else None

        # Check if application ID exists
        if application_id is not None:
            # Delete personal information associated with the retrieved application ID
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.personal_info
                    WHERE application_id = %s
                """, [application_id])
            return HttpResponse(f"Personal information for {username} has been deleted.")
        else:
            return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")



def updatePersonalInfoRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using raw SQL query
            query_application_id = f"""
                SELECT af.application_id 
                FROM public.user_table u
                INNER JOIN public.student s ON u.user_id = s.user_id
                INNER JOIN public.application_form af ON s.student_id = af.student_id
                WHERE u.user_name = '{username}'
                AND af.application_id IS NOT NULL
                LIMIT 1
            """
            cursor.execute(query_application_id)
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'update'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdatePersonalInfo.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")


def updatePersonalInfo(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id from the form input
            application_id = request.POST.get('application_id')

            # Retrieve the updated fields from the form input
            updated_fields = {}

            # List of fields that can be updated
            allowed_fields = ['name', 'full_name', 'legal_name', 'maiden_name', 'image']

            # Iterate through allowed fields and add to updated_fields if provided and selected for update
            for field in allowed_fields:
                update_field = f"update_{field}"
                if update_field in request.POST and request.POST.get(update_field) == "true":
                    if field == 'image' and field in request.FILES:
                        updated_fields[field] = request.FILES[field].read()
                    else:
                        updated_fields[field] = request.POST.get(field)

            # Construct the SQL query to update the personal info
            update_query = """
                UPDATE public.personal_info
                SET {}
                WHERE application_id = %s
            """.format(', '.join([f"{field} = %s" for field in updated_fields]))

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, [v for k, v in updated_fields.items()] + [application_id])

            return HttpResponse("Personal information updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")



# for biological info


def addBiologicalInfoRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            query_application_id = f"SELECT public.get_application_id('{username}')"
            cursor.execute(query_application_id)
            application_id = cursor.fetchone()

            if application_id:
                application_id = application_id[0]  # Extract the application_id from the result tuple
                print(application_id)
                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateBiologicalInfo.html', context)

            else:
                return HttpResponse("No application found for the student.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def addBiologicalInfo(request, username):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Retrieve the form data from the POST request
                application_id = request.POST.get('application_id')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                date_of_birth = request.POST.get('date_of_birth')
                place_of_birth = request.POST.get('place_of_birth')
                country_of_birth = request.POST.get('country_of_birth')
                city_of_birth = request.POST.get('city_of_birth')
                gender = request.POST.get('gender')
                blood_type = request.POST.get('blood_type')
                height = request.POST.get('height')
                weight = request.POST.get('weight')
                hair_color = request.POST.get('hair_color')
                eye_color = request.POST.get('eye_color')
                handedness = request.POST.get('handedness')
                marital_status = request.POST.get('marital_status')
                religion = request.POST.get('religion')
                ethnicity = request.POST.get('ethnicity')
                nationality = request.POST.get('nationality')
                native_language = request.POST.get('native_language')
                citizenship = request.POST.get('citizenship')
                disability = request.POST.get('disability')
                medical_reports = request.FILES.get('medical_reports')
                # Check if all required fields are provided
                if application_id is not None:  # Insert into biological_info table
                    cursor.execute("""
                        INSERT INTO public.biological_info (first_name, last_name, date_of_birth, place_of_birth, country_of_birth, 
                        city_of_birth, gender, blood_type, height, weight, hair_color, eye_color, handedness, marital_status, religion, 
                        ethnicity, nationality, native_language, citizenship, disability, application_id, medical_reports)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [first_name, last_name, date_of_birth, place_of_birth, country_of_birth, city_of_birth, gender,
                          blood_type, height, weight, hair_color, eye_color, handedness, marital_status, religion, ethnicity,
                          nationality, native_language, citizenship, disability, application_id, medical_reports.read()])
                    
                    # Update last_filled_table to 'biological_info'
                    cursor.execute("""
                        UPDATE public.application_form
                        SET last_filled_table = 'biological_info'
                        WHERE application_id = %s
                    """, [application_id])
                    
                    # Redirect to some success page
                    return redirect('addContactInfoRenderer', username=username)
                else:
                    return HttpResponse("Missing required fields.")
                
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")
    
    
    
def seeBiologicalInfo(request, username):
    try:
        # Retrieve biological information for the given username
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT first_name, last_name, date_of_birth, place_of_birth, country_of_birth,
                       city_of_birth, gender, blood_type, height, weight, hair_color,
                       eye_color, handedness, marital_status, religion, ethnicity,
                       nationality, native_language, citizenship, disability, medical_reports
                FROM public.biological_info
                WHERE application_id = (
                    SELECT af.application_id 
                    FROM public.student s 
                    INNER JOIN public.application_form af ON s.student_id = af.student_id 
                    INNER JOIN public.user_table u ON s.user_id = u.user_id
                    WHERE u.user_name = %s AND af.application_id IS NOT NULL
                    LIMIT 1
                )
            """, [username])
            biological_info = cursor.fetchone()

        # Check if biological information exists
        if biological_info:
            # Extract medical reports
            first_name, last_name, date_of_birth, place_of_birth, country_of_birth, \
            city_of_birth, gender, blood_type, height, weight, hair_color, \
            eye_color, handedness, marital_status, religion, ethnicity, \
            nationality, native_language, citizenship, disability, medical_reports = biological_info
            
            # Convert medical reports to Base64 encoding
            medical_reports_base64 = base64.b64encode(medical_reports).decode('utf-8') if medical_reports else None
            
            # Pass the retrieved biological information to the HTML template
            context = {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'date_of_birth': date_of_birth,
                'place_of_birth': place_of_birth,
                'country_of_birth': country_of_birth,
                'city_of_birth': city_of_birth,
                'gender': gender,
                'blood_type': blood_type,
                'height': height,
                'weight': weight,
                'hair_color': hair_color,
                'eye_color': eye_color,
                'handedness': handedness,
                'marital_status': marital_status,
                'religion': religion,
                'ethnicity': ethnicity,
                'nationality': nationality,
                'native_language': native_language,
                'citizenship': citizenship,
                'disability': disability,
                'medical_reports_base64': medical_reports_base64
            }
            return render(request, 'seeBiologicalInfo.html', context)
        else:
            return HttpResponse(f"No biological information found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}") 
    
    
def deleteBiologicalInfo(request, username):
    try:
        # Retrieve the application ID for the given username
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()
            application_id = row[0] if row else None

        # Check if application ID exists
        if application_id is not None:
            # Delete biological information associated with the retrieved application ID
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.biological_info
                    WHERE application_id = %s
                """, [application_id])
            return HttpResponse(f"Biological information for {username} has been deleted.")
        else:
            return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")


def updateBiologicalInfoRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using raw SQL query
            query_application_id = f"""
                SELECT af.application_id 
                FROM public.user_table u
                INNER JOIN public.student s ON u.user_id = s.user_id
                INNER JOIN public.application_form af ON s.student_id = af.student_id
                WHERE u.user_name = '{username}'
                AND af.application_id IS NOT NULL
                LIMIT 1
            """
            cursor.execute(query_application_id)
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'update'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateBiologicalInfo.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def updateBiologicalInfo(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id from the form input
            application_id = request.POST.get('application_id')

            # Retrieve the updated fields from the form input
            updated_fields = {}

            # List of fields that can be updated
            allowed_fields = ['first_name', 'last_name', 'date_of_birth', 'place_of_birth', 'country_of_birth',
                              'city_of_birth', 'gender', 'blood_type', 'height', 'weight', 'hair_color',
                              'eye_color', 'handedness', 'marital_status', 'religion', 'ethnicity',
                              'nationality', 'native_language', 'citizenship', 'disability', 'medical_reports']

            # Iterate through allowed fields and add to updated_fields if provided
            for field in allowed_fields:
                update_field_key = f"update_{field}"
                if update_field_key in request.POST:
                    if field == 'medical_reports' and field in request.FILES:
                        updated_fields[field] = request.FILES[field].read()
                    else:
                        updated_fields[field] = request.POST.get(field)

            # Construct the SET part of the SQL query
            set_query = ', '.join([f"{field} = %s" for field in updated_fields])

            # Construct the SQL query to update the biological info
            update_query = f"""
                UPDATE public.biological_info
                SET {set_query}
                WHERE application_id = %s
            """

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, list(updated_fields.values()) + [application_id])

            return HttpResponse("Biological information updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")












# for contact info
def addContactInfoRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Call the PostgreSQL function to retrieve the application_id
            cursor.execute("SELECT public.get_application_id(%s)", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]
                print(application_id)
                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateContactInfo.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")


def addContactInfo(request, username):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Retrieve the application_id from the POST data
                application_id = request.POST.get('application_id')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                alternative_mail = request.POST.get('alternative_mail')
                print(application_id, email, phone, alternative_mail)
                # Check if all required fields are provided
                if email and phone and application_id:
                    # Insert or update contact info
                    cursor.execute("""
                        INSERT INTO public.contact_info (email, phone, alternative_mail, application_id)
                        VALUES (%s, %s, %s, %s)
                    """, [email, phone, alternative_mail, application_id])

                    # Update last_filled_table to 'contact_info'
                    cursor.execute("""
                        UPDATE public.application_form
                        SET last_filled_table = 'contact_info'
                        WHERE student_id = (
                            SELECT s.student_id
                            FROM public.student s
                            INNER JOIN public.user_table u ON s.user_id = u.user_id
                            WHERE u.user_name = %s
                        )
                    """, [username])
                    
                    # Redirect to addBiologicalInfoRenderer and pass username
                    return redirect('addAddressRenderer', username=username)
                else:
                    return HttpResponse("Missing required fields.")
                
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")
    
    

    
def seeContactInfo(request, username):
    try:
        # Retrieve contact information for the given username
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT email, phone, alternative_mail
                FROM public.contact_info
                WHERE application_id = (
                    SELECT public.get_application_id(%s)
                )
            """, [username])
            contact_info = cursor.fetchone()

        # Check if contact information exists
        if contact_info:
            # Pass the retrieved contact information to the HTML template
            context = {
                'username': username,
                'email': contact_info[0],
                'phone': contact_info[1],
                'alternative_email': contact_info[2]
            }
            return render(request, 'seeContactInfo.html', context)
        else:
            return HttpResponse(f"No contact information found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")



def deleteContactInfo(request, username):
    try:
        # Retrieve the application ID for the given username
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()
            application_id = row[0] if row else None

        # Check if application ID exists
        if application_id is not None:
            # Delete contact information associated with the retrieved application ID
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.contact_info
                    WHERE application_id = %s
                """, [application_id])
            return HttpResponse(f"Contact information for {username} has been deleted.")
        else:
            return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")




def updateContactInfoRenderer(request, username):
    try:
        # Retrieve the application_id using the public.get_application_id function
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'update'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateContactInfo.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")




def updateContactInfo(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id from the form input
            application_id = request.POST.get('application_id')

            # Retrieve the updated contact fields from the form input
            updated_fields = {}

            # Checkboxes indicating which fields to update
            update_email = request.POST.get('update_email')
            update_phone = request.POST.get('update_phone')
            update_alternative_mail = request.POST.get('update_alternative_mail')

            # Populate the updated_fields dictionary based on checkbox selections
            if update_email:
                updated_fields['email'] = request.POST.get('email')
            if update_phone:
                updated_fields['phone'] = request.POST.get('phone')
            if update_alternative_mail:
                updated_fields['alternative_mail'] = request.POST.get('alternative_mail')

            # Construct the SQL query to update the contact info
            update_query = """
                UPDATE public.contact_info
                SET {}
                WHERE application_id = %s
            """.format(', '.join([f"{field} = %s" for field in updated_fields]))

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, [v for k, v in updated_fields.items()] + [application_id])

            return HttpResponse("Contact information updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")













#for address
def addAddressRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Call the PostgreSQL function to retrieve the application_id
            cursor.execute("SELECT public.get_application_id(%s)", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]
                print(application_id)
                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateAddress.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def addAddress(request,username):
    if request.method == 'POST':
        try:
            # Retrieve address data from POST request
            country = request.POST.get('country')
            city = request.POST.get('city')
            street = request.POST.get('street')
            post_code = request.POST.get('post_code')
            application_id = request.POST.get('application_id')

            with connection.cursor() as cursor:
                # Insert address data into the database using raw SQL
                cursor.execute("""
                    INSERT INTO public.address (country, city, street, post_code, application_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, [country, city, street, post_code, application_id])

                # Update last_filled_table to 'address'
                cursor.execute("""
                    UPDATE public.application_form
                    SET last_filled_table = 'address'
                    WHERE student_id = (
                        SELECT s.student_id
                        FROM public.student s
                        INNER JOIN public.user_table u ON s.user_id = u.user_id
                        WHERE u.user_name = %s
                    )
                """, [username])

            # Assuming you want to redirect to another page after adding the address
            return redirect('addCitizenshipInfoRenderer',username=username)  # Replace 'some_other_view' with the name of your view

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("This is the add address view.")
    
def seeAddress(request, username):
    try:
        # Retrieve address information for the given username
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT country, city, street, post_code
                FROM public.address
                WHERE application_id = (
                    SELECT public.get_application_id(%s)
                )
            """, [username])
            address_info = cursor.fetchone()

        # Check if address information exists
        if address_info:
            # Pass the retrieved address information to the HTML template
            context = {
                'username': username,
                'country': address_info[0],
                'city': address_info[1],
                'street': address_info[2],
                'post_code': address_info[3]
            }
            return render(request, 'seeAddress.html', context)
        else:
            return HttpResponse(f"No address information found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def deleteAddress(request, username):
    try:
        # Retrieve the application ID for the given username
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()
            application_id = row[0] if row else None

        # Check if application ID exists
        if application_id is not None:
            # Delete address information associated with the retrieved application ID
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.address
                    WHERE application_id = %s
                """, [application_id])
            return HttpResponse(f"Address information for {username} has been deleted.")
        else:
            return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def updateAddressRenderer(request, username):
    try:
        # Retrieve the application_id using the public.get_application_id function
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'update'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateAddress.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def updateAddress(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id from the form input
            application_id = request.POST.get('application_id')

            # Retrieve the updated address fields from the form input
            updated_fields = {}

            # Checkboxes indicating which fields to update
            update_country = request.POST.get('update_country')
            update_city = request.POST.get('update_city')
            update_street = request.POST.get('update_street')
            update_post_code = request.POST.get('update_post_code')

            # Populate the updated_fields dictionary based on checkbox selections
            if update_country:
                updated_fields['country'] = request.POST.get('new_country')
            if update_city:
                updated_fields['city'] = request.POST.get('new_city')
            if update_street:
                updated_fields['street'] = request.POST.get('new_street')
            if update_post_code:
                updated_fields['post_code'] = request.POST.get('new_post_code')

            # Construct the SQL query to update the address info
            update_query = """
                UPDATE public.address
                SET {}
                WHERE application_id = %s
            """.format(', '.join([f"{field} = %s" for field in updated_fields]))

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, [v for k, v in updated_fields.items()] + [application_id])

            return HttpResponse("Address information updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")












# for citizenship info
def addCitizenshipInfoRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Call the PostgreSQL function to retrieve the application_id
            cursor.execute("SELECT public.get_application_id(%s)", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateCitizenshipInfo.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")


def addCitizenshipInfo(request, username):
    if request.method == 'POST':
        try:
            # Retrieve citizenship info data from POST request
            passport = request.POST.get('passport')
            dual_citizenship_status = request.POST.get('dual_citizenship_status')
            citizenship_number = request.POST.get('citizenship_number')
            application_id = request.POST.get('application_id')

            with connection.cursor() as cursor:
                # Insert citizenship info data into the database using raw SQL
                cursor.execute("""
                    INSERT INTO public.citizenship_info (passport, dual_citizenship_status, citizenship_number, application_id)
                    VALUES (%s, %s, %s, %s)
                """, [passport, dual_citizenship_status, citizenship_number, application_id])

                # Update last_filled_table to 'citizenship_info'
                cursor.execute("""
                    UPDATE public.application_form
                    SET last_filled_table = 'citizenship_info'
                    WHERE student_id = (
                        SELECT s.student_id
                        FROM public.student s
                        INNER JOIN public.user_table u ON s.user_id = u.user_id
                        WHERE u.user_name = %s
                    )
                """, [username])

            # Assuming you want to redirect to another page after adding citizenship info
            return redirect('addAcademicRecordRenderer', username=username)

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("This is the add citizenship info view.")
    
    
    
def seeCitizenshipInfo(request, username):
    try:
        # Retrieve citizenship information for the given username
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT passport, dual_citizenship_status, citizenship_number
                FROM public.citizenship_info
                WHERE application_id = (
                    SELECT public.get_application_id(%s)
                )
            """, [username])
            citizenship_info = cursor.fetchone()

        # Check if citizenship information exists
        if citizenship_info:
            # Pass the retrieved citizenship information to the HTML template
            context = {
                'username': username,
                'passport': citizenship_info[0],
                'dual_citizenship_status': citizenship_info[1],
                'citizenship_number': citizenship_info[2]
            }
            return render(request, 'seeCitizenshipInfo.html', context)
        else:
            return HttpResponse(f"No citizenship information found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
    
    
    
def deleteCitizenshipInfo(request, username):
    try:
        # Retrieve the application ID for the given username
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()
            application_id = row[0] if row else None

        # Check if application ID exists
        if application_id is not None:
            # Delete citizenship information associated with the retrieved application ID
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.citizenship_info
                    WHERE application_id = %s
                """, [application_id])
            return HttpResponse(f"Citizenship information for {username} has been deleted.")
        else:
            return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")




def updateCitizenshipInfoRenderer(request, username):
    try:
        # Retrieve the application_id using the public.get_application_id function
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'update'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateCitizenshipInfo.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")





def updateCitizenshipInfo(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id from the form input
            application_id = request.POST.get('application_id')

            # Retrieve the updated citizenship fields from the form input
            updated_fields = {}

            # Checkboxes indicating which fields to update
            update_passport = request.POST.get('update_passport')
            update_dual_citizenship = request.POST.get('update_dual_citizenship')
            update_citizenship_number = request.POST.get('update_citizenship_number')

            # Populate the updated_fields dictionary based on checkbox selections
            if update_passport:
                updated_fields['passport'] = request.POST.get('new_passport')
            if update_dual_citizenship:
                updated_fields['dual_citizenship_status'] = request.POST.get('new_dual_citizenship')
            if update_citizenship_number:
                updated_fields['citizenship_number'] = request.POST.get('new_citizenship_number')

            # Construct the SQL query to update the citizenship info
            update_query = """
                UPDATE public.citizenship_info
                SET {}
                WHERE application_id = %s
            """.format(', '.join([f"{field} = %s" for field in updated_fields]))

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, [v for k, v in updated_fields.items()] + [application_id])

            return HttpResponse("Citizenship information updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")




















# for academic record
def addAcademicRecordRenderer(request, username):
    try:
        is_post_request = False  # Initialize as False by default

        if request.method == 'POST':
            is_post_request = True  # Mark as true if it's a POST request
            print("This is a POST request.")

            # Handle the form submission here

        with connection.cursor() as cursor:
            # Call the PostgreSQL function to retrieve the application_id
            cursor.execute("SELECT public.get_application_id(%s)", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                    'is_post_request': is_post_request,  # Include whether the request is a POST request or not
                }
                return render(request, 'addOrUpdateAcademicRecord.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")



def addAcademicRecord(request, username):
    if request.method == 'POST':
        try:
            # Retrieve academic record data from POST request
            institution = request.POST.get('institution')
            country = request.POST.get('country')
            city = request.POST.get('city')
            dates_attended = request.POST.get('dates_attended')
            level_of_study = request.POST.get('level_of_study')
            format_of_study = request.POST.get('format_of_study')
            gpa_explanation = request.POST.get('gpa_explanation')
            transcript = request.FILES.get('transcript')
            application_id = request.POST.get('application_id')
            
            # Set default value of is_post_request to False if not provided in POST
            is_post_request = request.POST.get('is_post_request', False)
            
            print(is_post_request)
            with connection.cursor() as cursor:
                # Insert academic record data into the database using raw SQL
                cursor.execute("""
                    INSERT INTO public.academic_record (institution, country, city, dates_attended, level_of_study, format_of_study, gpa_explanation, transcript, application_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [institution, country, city, dates_attended, level_of_study, format_of_study, gpa_explanation, transcript.read(), application_id])

            if is_post_request == True:
                return HttpResponse("Received POST request but not performing insertion.")
                
                # Update last_filled_table to 'academic_record'
                cursor.execute("""
                    UPDATE public.application_form
                    SET last_filled_table = 'academic_record'
                    WHERE student_id = (
                        SELECT s.student_id
                        FROM public.student s
                        INNER JOIN public.user_table u ON s.user_id = u.user_id
                        WHERE u.user_name = %s
                    )
                """, [username])
            
            # Assuming you want to redirect to another page after adding academic record
            return redirect('AddOneMoreOrMove', username=username)

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("This is the add academic record view.")

    
        
def seeAcademicRecord(request, username):
    try:
        # Retrieve academic records for the given username
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT record_id, institution, country, city, dates_attended, level_of_study,
                       format_of_study, gpa_explanation, transcript
                FROM public.academic_record
                WHERE application_id = (
                    SELECT public.get_application_id(%s)
                )
            """, [username])
            academic_records = cursor.fetchall()

        # Check if academic records exist
        if academic_records:
            # Modify academic records to handle transcript field
            modified_academic_records = []
            for record in academic_records:
                modified_record = list(record)  # Convert tuple to list
                if modified_record[8]:  # Check if transcript field is not empty
                    pdf_blob_base64 = base64.b64encode(modified_record[8]).decode('utf-8')
                    modified_record[8] = pdf_blob_base64
                modified_academic_records.append(tuple(modified_record))  # Convert list back to tuple

            # Pass the modified academic records to the HTML template
            context = {
                'username': username,
                'academic_records': modified_academic_records,
            }
            return render(request, 'seeAllAcademicRecords.html', context)
        else:
            return HttpResponse(f"No academic records found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")


def deleteAcademicRecord(request, username):
    if request.method == 'POST':
        try:
            # Retrieve record_id from POST request
            record_id = request.POST.get('record_id')

            # Delete academic record based on record_id
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.academic_record
                    WHERE record_id = %s
                """, [record_id])

            return HttpResponse(f"Academic record with ID {record_id} has been deleted.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("This is the delete academic record view. Please use POST method to delete a record.")
    
    
def updateAcademicRecordRenderer(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id using the public.get_application_id function
            with connection.cursor() as cursor:
                cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
                row = cursor.fetchone()

                if row and row[0]:  # Check if the row exists and application_id is not null
                    application_id = row[0]
                    record_id = request.POST.get('record_id')

                    # Rendering part
                    workType = 'update'
                    context = {
                        'username': username,
                        'workType': workType,
                        'application_id': application_id,  # Include the application_id in the context
                        'record_id': record_id,  # Include the record_id in the context
                    }
                    return render(request, 'addOrUpdateAcademicRecord.html', context)

                else:
                    return HttpResponse("No application found for the student or application_id is null.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("This view only accepts POST requests.")

def updateAcademicRecord(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id and record_id from the form input
            application_id = request.POST.get('application_id')
            record_id = request.POST.get('record_id')

            # Convert record_id to an integer
            record_id = int(record_id)

            # Retrieve the updated academic fields from the form input
            updated_fields = {}

            # Checkboxes indicating which fields to update
            update_institution = request.POST.get('update_institution')
            update_country = request.POST.get('update_country')
            update_city = request.POST.get('update_city')
            update_dates_attended = request.POST.get('update_dates_attended')
            update_level_of_study = request.POST.get('update_level_of_study')
            update_format_of_study = request.POST.get('update_format_of_study')
            update_gpa_explanation = request.POST.get('update_gpa_explanation')
            update_transcript = request.FILES.get('transcript')

            # Populate the updated_fields dictionary based on checkbox selections
            if update_institution:
                updated_fields['institution'] = request.POST.get('institution')
            if update_country:
                updated_fields['country'] = request.POST.get('country')
            if update_city:
                updated_fields['city'] = request.POST.get('city')
            if update_dates_attended:
                updated_fields['dates_attended'] = request.POST.get('dates_attended')
            if update_level_of_study:
                updated_fields['level_of_study'] = request.POST.get('level_of_study')
            if update_format_of_study:
                updated_fields['format_of_study'] = request.POST.get('format_of_study')
            if update_gpa_explanation:
                updated_fields['gpa_explanation'] = request.POST.get('gpa_explanation')
            if update_transcript:
                updated_fields['transcript'] = update_transcript.read()

            # Construct the SET part of the SQL query
            set_query = ', '.join([f"{field} = %s" for field in updated_fields])

            # Construct the SQL query to update the academic record
            update_query = f"""
                UPDATE public.academic_record
                SET {set_query}
                WHERE record_id = %s
            """

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, [v for v in updated_fields.values()] + [record_id])

            return HttpResponse("Academic record updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")


def AddOneMoreOrMove(request, username):
    return render(request, 'AddOneMoreOrMove.html', {'username': username})





# for portfolio
def addPortfolioRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            query_application_id = f"SELECT public.get_application_id('{username}')"
            cursor.execute(query_application_id)
            application_id = cursor.fetchone()

            if application_id:
                application_id = application_id[0]  # Extract the application_id from the result tuple
                print(application_id)
                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdatePortfolio.html', context)

            else:
                return HttpResponse("No application found for the student.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def addPortfolio(request, username):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Retrieve the form data from the POST request
                application_id = request.POST.get('application_id')
                linked_in = request.POST.get('linked_in')
                extra_curricular_activity = request.POST.get('extra_curricular_activity')
                resume = request.FILES.get('resume')
                
                # Check if all required fields are provided
                if application_id is not None and resume is not None:
                    # Insert into portfolio table
                    cursor.execute("""
                        INSERT INTO public.portfolio (linked_in, extra_curricular_activity, application_id, resume)
                        VALUES (%s, %s, %s, %s)
                    """, [linked_in, extra_curricular_activity, application_id, resume.read()])
                    
                    # Update last_filled_table to 'portfolio'
                    cursor.execute("""
                        UPDATE public.application_form
                        SET last_filled_table = 'portfolio'
                        WHERE application_id = %s
                    """, [application_id])
                    
                    # Redirect to some success page
                    return redirect('addGMATRenderer', username=username)
                else:
                    return HttpResponse("Missing required fields.")
                
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")
   
def seePortfolio(request, username):
    try:
        # Retrieve portfolio information for the given username
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            query_application_id = f"SELECT public.get_application_id('{username}')"
            cursor.execute(query_application_id)
            application_id = cursor.fetchone()

            if application_id:
                application_id = application_id[0]  # Extract the application_id from the result tuple
                
                cursor.execute("""
                    SELECT linked_in, extra_curricular_activity, resume
                    FROM public.portfolio
                    WHERE application_id = %s
                    LIMIT 1
                """, [application_id])
                portfolio_info = cursor.fetchone()

                # Check if portfolio information exists
                if portfolio_info:
                    linked_in, extra_curricular_activity, resume = portfolio_info
                    
                    # Convert resume to Base64 encoding
                    resume_base64 = base64.b64encode(resume).decode('utf-8') if resume else None
                    
                    # Pass the retrieved portfolio information to the HTML template
                    context = {
                        'username': username,
                        'linked_in': linked_in,
                        'extra_curricular_activity': extra_curricular_activity,
                        'resume_base64': resume_base64,
                    }
                    return render(request, 'seePortfolio.html', context)
                else:
                    return HttpResponse(f"No portfolio information found for user {username}.")
            else:
                return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
    
    
def deletePortfolio(request, username):
    try:
        # Retrieve the application ID for the given username
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()
            application_id = row[0] if row else None

        # Check if application ID exists
        if application_id is not None:
            # Delete portfolio information associated with the retrieved application ID
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.portfolio
                    WHERE application_id = %s
                """, [application_id])
            return HttpResponse(f"Portfolio information for {username} has been deleted.")
        else:
            return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def updatePortfolioRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'update'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdatePortfolio.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def updatePortfolio(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id from the form input
            application_id = request.POST.get('application_id')

            # Retrieve the updated fields from the form input
            updated_fields = {}

            # List of fields that can be updated
            allowed_fields = ['linked_in', 'extra_curricular_activity', 'resume']

            # Iterate through allowed fields and add to updated_fields if provided
            for field in allowed_fields:
                update_field_key = f"update_{field}"
                if update_field_key in request.POST:
                    if field == 'resume' and field in request.FILES:
                        updated_fields[field] = request.FILES[field].read()
                    else:
                        updated_fields[field] = request.POST.get(field)

            # Construct the SET part of the SQL query
            set_query = ', '.join([f"{field} = %s" for field in updated_fields])

            # Construct the SQL query to update the portfolio
            update_query = f"""
                UPDATE public.portfolio
                SET {set_query}
                WHERE application_id = %s
            """

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, list(updated_fields.values()) + [application_id])

            return HttpResponse("Portfolio information updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")




# for GMAT
def addGMATRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            query_application_id = f"SELECT public.get_application_id('{username}')"
            cursor.execute(query_application_id)
            application_id = cursor.fetchone()

            if application_id:
                application_id = application_id[0]  # Extract the application_id from the result tuple
                print(application_id)
                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateGMATscore.html', context)

            else:
                return HttpResponse("No application found for the student.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def addGMAT(request, username):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Retrieve the form data from the POST request
                application_id = request.POST.get('application_id')
                test_center = request.POST.get('test_center')
                quantitative_score = request.POST.get('quantitative_score')
                verbal_score = request.POST.get('verbal_score')
                integrated_reasoning_score = request.POST.get('integrated_reasoning_score')
                analytical_writing_score = request.POST.get('analytical_writing_score')
                test_date = request.POST.get('test_date')
                transcript = request.FILES.get('transcript')
                
                # Check if all required fields are provided
                if application_id is not None and test_center is not None and quantitative_score is not None \
                        and verbal_score is not None and integrated_reasoning_score is not None \
                        and analytical_writing_score is not None and test_date is not None and transcript is not None:
                    # Insert into gmat_score table
                    cursor.execute("""
                        INSERT INTO public.gmat_score (test_date, test_center, quantitative_score, verbal_score,
                        integrated_reasoning_score, analytical_writing_score, application_id, transcript)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [test_date, test_center, quantitative_score, verbal_score,
                          integrated_reasoning_score, analytical_writing_score, application_id, transcript.read()])
                    
                    # Update last_filled_table to 'gmat_score'
                    cursor.execute("""
                        UPDATE public.application_form
                        SET last_filled_table = 'gmat_score'
                        WHERE application_id = %s
                    """, [application_id])
                    
                    # Redirect to some success page
                    return redirect('addGRERenderer', username=username)
                else:
                    return HttpResponse("Missing required fields.")
                
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")   
    
    
def seeGMAT(request, username):
    try:
        # Retrieve GMAT information for the given username
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            query_application_id = f"SELECT public.get_application_id('{username}')"
            cursor.execute(query_application_id)
            application_id = cursor.fetchone()

            if application_id:
                application_id = application_id[0]  # Extract the application_id from the result tuple
                
                cursor.execute("""
                    SELECT test_date, test_center, quantitative_score, verbal_score,
                    integrated_reasoning_score, analytical_writing_score, transcript
                    FROM public.gmat_score
                    WHERE application_id = %s
                    LIMIT 1
                """, [application_id])
                gmat_info = cursor.fetchone()

                # Check if GMAT information exists
                if gmat_info:
                    test_date, test_center, quantitative_score, verbal_score, \
                        integrated_reasoning_score, analytical_writing_score, transcript = gmat_info
                    
                    # Convert transcript to Base64 encoding
                    transcript_base64 = base64.b64encode(transcript).decode('utf-8') if transcript else None
                    
                    # Pass the retrieved GMAT information to the HTML template
                    context = {
                        'username': username,
                        'test_date': test_date,
                        'test_center': test_center,
                        'quantitative_score': quantitative_score,
                        'verbal_score': verbal_score,
                        'integrated_reasoning_score': integrated_reasoning_score,
                        'analytical_writing_score': analytical_writing_score,
                        'transcript_base64': transcript_base64,
                    }
                    return render(request, 'seeGMAT.html', context)
                else:
                    return HttpResponse(f"No GMAT information found for user {username}.")
            else:
                return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
    
def deleteGMAT(request, username):
    try:
        # Retrieve the application ID for the given username
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()
            application_id = row[0] if row else None

        # Check if application ID exists
        if application_id is not None:
            # Delete GMAT information associated with the retrieved application ID
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.gmat_score
                    WHERE application_id = %s
                """, [application_id])
            return HttpResponse(f"GMAT information for {username} has been deleted.")
        else:
            return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def updateGMATRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'update'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateGMATscore.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")



def updateGMAT(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id from the form input
            application_id = request.POST.get('application_id')

            # Retrieve the updated fields from the form input
            updated_fields = {}

            # List of fields that can be updated
            allowed_fields = ['test_center', 'quantitative_score', 'verbal_score', 'integrated_reasoning_score', 'analytical_writing_score', 'test_date', 'transcript']

            # Iterate through allowed fields and add to updated_fields if provided
            for field in allowed_fields:
                update_field_key = f"update_{field}"
                if update_field_key in request.POST:
                    if field == 'transcript' and field in request.FILES:
                        updated_fields[field] = request.FILES[field].read()
                    else:
                        updated_fields[field] = request.POST.get(field)

            # Construct the SET part of the SQL query
            set_query = ', '.join([f"{field} = %s" for field in updated_fields])

            # Construct the SQL query to update the GMAT information
            update_query = f"""
                UPDATE public.gmat_score
                SET {set_query}
                WHERE application_id = %s
            """

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, list(updated_fields.values()) + [application_id])

            return HttpResponse("GMAT information updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")

# for gre


def addGRERenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            query_application_id = f"SELECT public.get_application_id('{username}')"
            cursor.execute(query_application_id)
            application_id = cursor.fetchone()

            if application_id:
                application_id = application_id[0]  # Extract the application_id from the result tuple
                
                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateGREscore.html', context)

            else:
                return HttpResponse("No application found for the student.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
    
def addGRE(request, username):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Retrieve the form data from the POST request
                application_id = request.POST.get('application_id')
                test_center = request.POST.get('test_center')
                verbal_score = request.POST.get('verbal_score')
                quantitative_score = request.POST.get('quantitative_score')
                analytical_writing_score = request.POST.get('analytical_score')  # Corrected field name
                test_date = request.POST.get('test_date')
                transcript = request.FILES.get('transcript')
                
                # Check if all required fields are provided
                if application_id != '' and test_center != '' and verbal_score != '' \
                        and quantitative_score != '' and analytical_writing_score != '' \
                        and test_date != '' and transcript is not None:  # Checking if transcript is not None
                    # Insert into gre_score table
                    cursor.execute("""
                        INSERT INTO public.gre_score (test_date, test_center, verbal_score, quantitative_score,
                        analytical_score, application_id, transcript)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, [test_date, test_center, verbal_score, quantitative_score,
                          analytical_writing_score, application_id, transcript.read()])

                    # Update last_filled_table to 'gre_score'
                    cursor.execute("""
                        UPDATE public.application_form
                        SET last_filled_table = 'gre_score'
                        WHERE application_id = %s
                    """, [application_id])
                    
                    # Redirect to some success page
                    return redirect('addIELTSRenderer', username=username)
                else:
                    return HttpResponse("Missing required fields.")
                
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")

def seeGRE(request, username):
    try:
        # Retrieve GRE information for the given username
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            query_application_id = f"SELECT public.get_application_id('{username}')"
            cursor.execute(query_application_id)
            application_id = cursor.fetchone()

            if application_id:
                application_id = application_id[0]  # Extract the application_id from the result tuple
                
                # Query GRE information from the database
                cursor.execute("""
                    SELECT test_date, test_center, verbal_score, quantitative_score,
                    analytical_score, transcript
                    FROM public.gre_score
                    WHERE application_id = %s
                    LIMIT 1
                """, [application_id])
                gre_info = cursor.fetchone()

                # Check if GRE information exists
                if gre_info:
                    test_date, test_center, verbal_score, quantitative_score, \
                        analytical_score, transcript = gre_info
                    
                    # Convert transcript to Base64 encoding
                    transcript_base64 = base64.b64encode(transcript).decode('utf-8') if transcript else None
                    
                    # Pass the retrieved GRE information to the HTML template
                    context = {
                        'username': username,
                        'test_date': test_date,
                        'test_center': test_center,
                        'verbal_score': verbal_score,
                        'quantitative_score': quantitative_score,
                        'analytical_score': analytical_score,
                        'transcript_base64': transcript_base64,
                    }
                    return render(request, 'seeGRE.html', context)
                else:
                    return HttpResponse(f"No GRE information found for user {username}.")
            else:
                return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
        
def deleteGRE(request, username):
    try:
        # Retrieve the application ID for the given username
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()
            application_id = row[0] if row else None

        # Check if application ID exists
        if application_id is not None:
            # Delete GRE information associated with the retrieved application ID
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.gre_score
                    WHERE application_id = %s
                """, [application_id])
            return HttpResponse(f"GRE information for {username} has been deleted.")
        else:
            return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
    
    
    
def updateGRERenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'update'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateGREscore.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
    
    
    
def updateGRE(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id from the form input
            application_id = request.POST.get('application_id')

            # Retrieve the updated fields from the form input
            updated_fields = {}

            # List of fields that can be updated
            allowed_fields = ['test_center', 'verbal_score', 'quantitative_score', 'analytical_score', 'test_date', 'transcript']

            # Iterate through allowed fields and add to updated_fields if provided
            for field in allowed_fields:
                update_field_key = f"update_{field}"
                if update_field_key in request.POST:
                    if field == 'transcript' and field in request.FILES:
                        updated_fields[field] = request.FILES[field].read()
                    else:
                        updated_fields[field] = request.POST.get(field)

            # Construct the SET part of the SQL query
            set_query = ', '.join([f"{field} = %s" for field in updated_fields])

            # Construct the SQL query to update the GRE information
            update_query = f"""
                UPDATE public.gre_score
                SET {set_query}
                WHERE application_id = %s
            """

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, list(updated_fields.values()) + [application_id])

            return HttpResponse("GRE information updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")








# IELTS views
def addIELTSRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            query_application_id = f"SELECT public.get_application_id('{username}')"
            cursor.execute(query_application_id)
            application_id = cursor.fetchone()

            if application_id:
                application_id = application_id[0]  # Extract the application_id from the result tuple
                
                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateIELTSscore.html', context)

            else:
                return HttpResponse("No application found for the student.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def addIELTS(request, username):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Retrieve the form data from the POST request
                application_id = request.POST.get('application_id')
                test_date = request.POST.get('test_date')
                test_center = request.POST.get('test_center')
                writing_score = request.POST.get('writing_score')
                listening_score = request.POST.get('listening_score')
                speaking_score = request.POST.get('speaking_score')
                reading_score = request.POST.get('reading_score')
                transcript = request.FILES.get('transcript')
                
                # Check if all required fields are provided
                if application_id is not None and test_date is not None and test_center is not None \
                        and writing_score is not None and listening_score is not None \
                        and speaking_score is not None and reading_score is not None and transcript is not None:
                    # Insert into ielts_score table
                    cursor.execute("""
                        INSERT INTO public.ielts_score (test_date, test_center, writing_score,
                        listening_score, speaking_score, reading_score, application_id, transcript)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [test_date, test_center, writing_score, listening_score,
                          speaking_score, reading_score, application_id, transcript.read()])
                    
                    # Update last_filled_table to 'ielts_score'
                    cursor.execute("""
                        UPDATE public.application_form
                        SET last_filled_table = 'ielts_score'
                        WHERE application_id = %s
                    """, [application_id])
                    
                    # Redirect to some success page
                    return redirect('addTOEFLRenderer', username=username)
                else:
                    return HttpResponse("Missing required fields.")
                
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")

def seeIELTS(request, username):
    try:
        # Retrieve IELTS information for the given username
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            query_application_id = f"SELECT public.get_application_id('{username}')"
            cursor.execute(query_application_id)
            application_id = cursor.fetchone()

            if application_id:
                application_id = application_id[0]  # Extract the application_id from the result tuple
                
                # Query IELTS information from the database
                cursor.execute("""
                    SELECT test_date, test_center, writing_score, listening_score,
                    speaking_score, reading_score, transcript
                    FROM public.ielts_score
                    WHERE application_id = %s
                    LIMIT 1
                """, [application_id])
                ielts_info = cursor.fetchone()

                # Check if IELTS information exists
                if ielts_info:
                    test_date, test_center, writing_score, listening_score, \
                        speaking_score, reading_score, transcript = ielts_info
                    
                    # Convert transcript to Base64 encoding
                    transcript_base64 = base64.b64encode(transcript).decode('utf-8') if transcript else None
                    
                    # Pass the retrieved IELTS information to the HTML template
                    context = {
                        'username': username,
                        'test_date': test_date,
                        'test_center': test_center,
                        'writing_score': writing_score,
                        'listening_score': listening_score,
                        'speaking_score': speaking_score,
                        'reading_score': reading_score,
                        'transcript_base64': transcript_base64,
                    }
                    return render(request, 'seeIELTS.html', context)
                else:
                    return HttpResponse(f"No IELTS information found for user {username}.")
            else:
                return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def deleteIELTS(request, username):
    try:
        # Retrieve the application ID for the given username
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()
            application_id = row[0] if row else None

        # Check if application ID exists
        if application_id is not None:
            # Delete IELTS information associated with the retrieved application ID
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.ielts_score
                    WHERE application_id = %s
                """, [application_id])
            return HttpResponse(f"IELTS information for {username} has been deleted.")
        else:
            return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def updateIELTSRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'update'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateIELTSscore.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def updateIELTS(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id from the form input
            application_id = request.POST.get('application_id')

            # Retrieve the updated fields from the form input
            updated_fields = {}

            # List of fields that can be updated
            allowed_fields = ['test_center', 'test_date', 'writing_score', 'listening_score',
                              'speaking_score', 'reading_score', 'transcript']

            # Iterate through allowed fields and add to updated_fields if provided
            for field in allowed_fields:
                update_field_key = f"update_{field}"
                if update_field_key in request.POST:
                    if field == 'transcript' and field in request.FILES:
                        updated_fields[field] = request.FILES[field].read()
                    else:
                        updated_fields[field] = request.POST.get(field)

            # Construct the SET part of the SQL query
            set_query = ', '.join([f"{field} = %s" for field in updated_fields])

            # Construct the SQL query to update the IELTS information
            update_query = f"""
                UPDATE public.ielts_score
                SET {set_query}
                WHERE application_id = %s
            """

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, list(updated_fields.values()) + [application_id])

            return HttpResponse("IELTS information updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")






# TOEFL views
def addTOEFLRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'add'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateTOEFLscore.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")




def addTOEFL(request, username):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Retrieve the form data from the POST request
                application_id = request.POST.get('application_id')
                test_date = request.POST.get('test_date')
                test_center = request.POST.get('test_center')
                writing_score = int(round(float(request.POST.get('writing_score'))))
                listening_score = int(round(float(request.POST.get('listening_score'))))
                speaking_score = int(round(float(request.POST.get('speaking_score'))))
                reading_score = int(round(float(request.POST.get('reading_score'))))
                transcript = request.FILES.get('transcript')
                
                # Check if all required fields are provided
                if application_id is not None and test_date is not None and test_center is not None \
                        and writing_score is not None and listening_score is not None \
                        and speaking_score is not None and reading_score is not None and transcript is not None:
                    # Insert into toefl table
                    cursor.execute("""
                        INSERT INTO public.toefl (test_date, test_center, writing_score,
                        listening_score, speaking_score, reading_score, application_id, transcript)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [test_date, test_center, writing_score, listening_score,
                          speaking_score, reading_score, application_id, transcript.read()])
                    
                    # Update last_filled_table to 'toefl'
                    cursor.execute("""
                        UPDATE public.application_form
                        SET last_filled_table = 'toefl'
                        WHERE application_id = %s
                    """, [application_id])
                    
                    # Redirect to some success page
                    return redirect('addProgramSelectionRenderer', username=username)
                    # return redirect('', username=username)
                else:
                    return HttpResponse("Missing required fields.")
                
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")

def seeTOEFL(request, username):
    try:
        # Retrieve TOEFL information for the given username
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            query_application_id = f"SELECT public.get_application_id('{username}')"
            cursor.execute(query_application_id)
            application_id = cursor.fetchone()

            if application_id:
                application_id = application_id[0]  # Extract the application_id from the result tuple
                
                # Query TOEFL information from the database
                cursor.execute("""
                    SELECT test_date, test_center, writing_score, listening_score,
                    speaking_score, reading_score, transcript
                    FROM public.toefl
                    WHERE application_id = %s
                    LIMIT 1
                """, [application_id])
                toefl_info = cursor.fetchone()

                # Check if TOEFL information exists
                if toefl_info:
                    test_date, test_center, writing_score, listening_score, \
                        speaking_score, reading_score, transcript = toefl_info
                    
                    # Convert transcript to Base64 encoding
                    transcript_base64 = base64.b64encode(transcript).decode('utf-8') if transcript else None
                    
                    # Pass the retrieved TOEFL information to the HTML template
                    context = {
                        'username': username,
                        'test_date': test_date,
                        'test_center': test_center,
                        'writing_score': writing_score,
                        'listening_score': listening_score,
                        'speaking_score': speaking_score,
                        'reading_score': reading_score,
                        'transcript_base64': transcript_base64,
                    }
                    return render(request, 'seeTOEFL.html', context)
                else:
                    return HttpResponse(f"No TOEFL information found for user {username}.")
            else:
                return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def deleteTOEFL(request, username):
    try:
        # Retrieve the application ID for the given username
        with connection.cursor() as cursor:
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()
            application_id = row[0] if row else None

        # Check if application ID exists
        if application_id is not None:
            # Delete TOEFL information associated with the retrieved application ID
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM public.toefl_score
                    WHERE application_id = %s
                """, [application_id])
            return HttpResponse(f"TOEFL information for {username} has been deleted.")
        else:
            return HttpResponse(f"No application found for user {username}.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")



def updateTOEFLRenderer(request, username):
    try:
        with connection.cursor() as cursor:
            # Retrieve the application_id using the get_application_id function
            cursor.execute("SELECT public.get_application_id(%s) AS application_id", [username])
            row = cursor.fetchone()

            if row and row[0]:  # Check if the row exists and application_id is not null
                application_id = row[0]

                # Rendering part
                workType = 'update'
                context = {
                    'username': username,
                    'workType': workType,
                    'application_id': application_id,  # Include the application_id in the context
                }
                return render(request, 'addOrUpdateTOEFLscore.html', context)

            else:
                return HttpResponse("No application found for the student or application_id is null.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")


def updateTOEFL(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the application_id from the form input
            application_id = request.POST.get('application_id')

            # Retrieve the updated fields from the form input
            updated_fields = {}

            # List of fields that can be updated
            allowed_fields = ['test_center', 'test_date', 'writing_score', 'listening_score',
                              'speaking_score', 'reading_score', 'transcript']

            # Iterate through allowed fields and add to updated_fields if provided
            for field in allowed_fields:
                update_field_key = f"update_{field}"
                if update_field_key in request.POST:
                    if field == 'transcript' and request.FILES.get('transcript'):
                        updated_fields[field] = request.FILES['transcript'].read()
                    else:
                        updated_fields[field] = request.POST.get(field)

            # Construct the SET part of the SQL query
            set_query = ', '.join([f"{field} = %s" for field in updated_fields])

            # Construct the SQL query to update the TOEFL information
            update_query = f"""
                UPDATE public.toefl
                SET {set_query}
                WHERE application_id = %s
            """

            # Execute the SQL query with parameters
            with connection.cursor() as cursor:
                cursor.execute(update_query, list(updated_fields.values()) + [application_id])

            return HttpResponse("TOEFL information updated successfully.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
    else:
        return HttpResponse("Invalid request method.")



# def application_by_username(request, username):
#     # Check if there is an application for the given student
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT COUNT(*) FROM public.application_form WHERE student_id IN (SELECT student_id FROM public.student WHERE name = %s)", [username])
#         row = cursor.fetchone()
#         has_application = row[0] > 0  # True if there is at least one application, False otherwise

#     return render(request, 'application_home_by_username.html', {'username': username, 'has_application': has_application})





# def create_application(request, username):
#     # Check if the student already has an application
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT COUNT(*) FROM public.application_form WHERE student_id = (SELECT student_id FROM public.student WHERE name = %s)", [username])
#         row = cursor.fetchone()
#         if row[0] > 0:
#             return HttpResponseRedirect(reverse('application_home_by_username', kwargs={'username': username}))

#     # Retrieve student_id from the student table based on the username
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT student_id FROM public.student WHERE name = %s", [username])
#         row = cursor.fetchone()
#         if row:
#             student_id = row[0]
#         else:
#             # Handle case where username doesn't exist in the student table
#             return HttpResponse("Student not found.")

#     # Get the current date for last_save_date
#     last_save_date = datetime.today()  # Use datetime instead of date

#     # Insert into application_form table
#     with connection.cursor() as cursor:
#         cursor.execute("INSERT INTO public.application_form (application_date, last_save_date, student_id) VALUES (NULL, %s, %s)", [last_save_date, student_id])

#     # Check if the insertion was successful
#     if cursor.rowcount > 0:
#         # Redirect to application home page
#         return HttpResponseRedirect(reverse('application_home_by_username', kwargs={'username': username}))
#     else:
#         # Handle case where insertion failed
#         return HttpResponse("Failed to create application.")
    
    
# def select_program(request, username):
#     print("Inside select_program view function")
#     if request.method == 'POST':
#         # Retrieve selected program IDs from the POST data
#         selected_program_ids = request.POST.getlist('selected_programs')
        
#         # Retrieve attributes of selected programs from the POST data
#         selected_program_names = request.POST.getlist('selected_program_names')
#         selected_program_tuition_fees = request.POST.getlist('selected_program_tuition_fees')
#         selected_program_durations = request.POST.getlist('selected_program_durations')
#         selected_program_application_deadlines = request.POST.getlist('selected_program_application_deadlines')
#         selected_program_programme_rankings = request.POST.getlist('selected_program_programme_rankings')
#         selected_program_department_names = request.POST.getlist('selected_program_department_names')
#         selected_program_department_heads = request.POST.getlist('selected_program_department_heads')
#         selected_program_established_dates = request.POST.getlist('selected_program_established_dates')
#         selected_program_university_names = request.POST.getlist('selected_program_university_names')
#         selected_program_university_locations = request.POST.getlist('selected_program_university_locations')
#         selected_program_university_established_dates = request.POST.getlist('selected_program_university_established_dates')
#         selected_program_university_ranks = request.POST.getlist('selected_program_university_ranks')
        
#         # Now you have all the attributes of selected programs, you can process them further
        
#         # For demonstration purposes, let's print them
#         print("Selected program IDs:", selected_program_ids)
#         print("Selected program names:", selected_program_names)
#         print("Selected program tuition fees:", selected_program_tuition_fees)
#         # Print other attributes as needed
        
#         # You can also retrieve the user from the username if needed
#         # user = User.objects.get(username=username)
        
#         # Return an HttpResponse or redirect to another page
#         return HttpResponse("Selected programs processed successfully")
#     else:
#         # Handle the case when the request method is not POST
#         return HttpResponse("Invalid request method")

# def update_application(request, username):
#     # Execute SQL query to fetch the required information
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SELECT 
#                 p.programme_name, p.tuition_fee, p.duration, p.application_deadline, p.programme_ranking,
#                 d.department_name, d.department_head, d.established_date,
#                 u.name AS university_name, u.location AS university_location, u.established_date AS university_established_date, u.rank AS university_rank
#             FROM 
#                 department d
#             INNER JOIN 
#                 university u ON d.university_id = u.university_id
#             INNER JOIN 
#                 programme p ON d.department_id = p.department_id
#         """)
#         rows = cursor.fetchall()

#     # Construct a list of dictionaries containing the fetched information
#     programs = []
#     for row in rows:
#         programme_name, tuition_fee, duration, application_deadline, programme_ranking, \
#         department_name, department_head, established_date, \
#         university_name, university_location, university_established_date, university_rank = row

#         program_info = {
#             'programme_name': programme_name,
#             'tuition_fee': tuition_fee,
#             'duration': duration,
#             'application_deadline': application_deadline,
#             'programme_ranking': programme_ranking,
#             'department_name': department_name,
#             'department_head': department_head,
#             'established_date': established_date,
#             'name': university_name,
#             'location': university_location,
#             'rank': university_rank
#         }
#         programs.append(program_info)

#     # Pass the fetched information to the HTML template
#     return render(request, '', {'username': username, 'programs': programs})
