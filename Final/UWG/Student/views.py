from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.db import connection

# def index(request):
#     # Get the username from the request
#     username = request.GET.get('username', '')

#     # Set the default year to 2020
#     year = 2020
#     search_clicked = False

#     if request.method == 'POST':
#         # If the form is submitted via POST, get the year value
#         year = request.POST.get('year', 2020)
#         # Set the search_clicked flag to True
#         search_clicked = True
#     # Execute the function to fetch program, department, and university IDs
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SELECT * FROM get_top_programs_and_departments_with_universities(%s);
#         """, [year])
#         program_ids = []
#         department_ids = []
#         university_ids = []
#         for row in cursor.fetchall():
#             program_ids.append(row[0])
#             department_ids.append(row[1])
#             university_ids.append(row[2])

#     # Join the tables and retrieve detailed information
#     programs_info = []
#     for program_id, department_id, university_id in zip(program_ids, department_ids, university_ids):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     p.programme_name, p.tuition_fee, p.duration, p.application_deadline, p.programme_ranking,
#                     d.department_name, d.department_head, d.established_date,
#                     u.name as university_name, u.location as university_location, u.established_date as university_established_date, u.rank as university_rank
#                 FROM 
#                     public.programme p
#                     INNER JOIN public.department d ON p.department_id = d.department_id
#                     INNER JOIN public.university u ON d.university_id = u.university_id
#                 WHERE 
#                     p.programme_id = %s;
#             """, [program_id])
#             program_info = cursor.fetchone()

#             programs_info.append({
#                 'programme_name': program_info[0],
#                 'tuition_fee': program_info[1],
#                 'duration': program_info[2],
#                 'application_deadline': program_info[3],
#                 'programme_ranking': program_info[4],
#                 'department_name': program_info[5],
#                 'department_head': program_info[6],
#                 'department_established_date': program_info[7],
#                 'university_name': program_info[8],
#                 'university_location': program_info[9],
#                 'university_established_date': program_info[10],
#                 'university_rank': program_info[11],
#             })

#     # Pass the fetched information and username to the HTML template
#     context = {
#         'programs_info': programs_info,
#         'username': username,
#     }
#     if search_clicked:
#         return redirect('StudentHome')
#     return render(request, 'StudentHomePage.html', context=context)
from django.shortcuts import render

def index(request):
    # Get the username from the request
    username = request.GET.get('username', '')

    # Pass the username to the HTML template
    context = {
        'username': username,
    }

    return render(request, 'StudentHomePage.html', context=context)


# views.py


def search_reports_rendererer(request, username):
    print(username)  # Just for debugging, remove in production
    return render(request, 'searchReportsHome.html', {'username': username})


# views.py


def search_reports_by_year(request,username):
    print(username)
    year = 2020  # Default year
    if request.method == 'POST':
        year = request.POST.get('year', 2020)

    # Execute the function to fetch reports for the given year
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM get_top_programs_and_departments_with_universities(%s);
        """, [year])
        program_ids = []
        department_ids = []
        university_ids = []
        for row in cursor.fetchall():
            program_ids.append(row[0])
            department_ids.append(row[1])
            university_ids.append(row[2])

    # Join the tables and retrieve detailed information
    programs_info = []
    for program_id, department_id, university_id in zip(program_ids, department_ids, university_ids):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.programme_name, p.tuition_fee, p.duration, p.application_deadline, p.programme_ranking,
                    d.department_name, d.department_head, d.established_date,
                    u.name as university_name, u.location as university_location, u.established_date as university_established_date, u.rank as university_rank
                FROM 
                    public.programme p
                    INNER JOIN public.department d ON p.department_id = d.department_id
                    INNER JOIN public.university u ON d.university_id = u.university_id
                WHERE 
                    p.programme_id = %s;
            """, [program_id])
            program_info = cursor.fetchone()

            programs_info.append({
                'programme_name': program_info[0],
                'tuition_fee': program_info[1],
                'duration': program_info[2],
                'application_deadline': program_info[3],
                'programme_ranking': program_info[4],
                'department_name': program_info[5],
                'department_head': program_info[6],
                'department_established_date': program_info[7],
                'university_name': program_info[8],
                'university_location': program_info[9],
                'university_established_date': program_info[10],
                'university_rank': program_info[11],
            })

    # Pass the fetched information and year to the HTML template
    context = {
        'programs_info': programs_info,
        'year': year,
        'username': username,
    }
    return render(request, 'reportsHome.html', context)
