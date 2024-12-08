from django.shortcuts import render
from django.http import JsonResponse
from .neo4j import Neo4jConnection  # Ensure the correct import path
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_user_progress(request):
    if request.method == "POST":
        try:
            # Parse the request data
            data = json.loads(request.body)
            user_id = data.get("user_id")
            page_id = data.get("page_id")
            completed = data.get("completed")

            # Validate the input
            if not user_id or not page_id:
                return JsonResponse({"success": False, "error": "Missing user_id or page_id"}, status=400)

            # Update the user's progress in Neo4j
            conn = Neo4jConnection()
            query = """
            MATCH (u:User {user_id: $user_id})-[r:PROGRESS]->(p:Page {id: $page_id})
            SET r.completed = $completed
            """
            conn.query(query, {"user_id": user_id, "page_id": page_id, "completed": completed})
            conn.close()

            return JsonResponse({"success": True, "message": "User progress updated successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)


import uuid

from django.views.decorators.csrf import csrf_exempt

from passlib.hash import bcrypt

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

@csrf_exempt
def signup(request):
    if request.method == "GET":
        # Render the signup.html page for GET requests
        return render(request, "signup.html")  # Ensure signup.html exists in your templates directory

    elif request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)

        # Generate a unique user ID using UUID
        user_id = str(uuid.uuid4())

        # Create the user in the database and set relationships
        conn = Neo4jConnection()
        try:
            user_query = """
            CREATE (u:User {user_id: $user_id, name: $name, email: $email, password: $password})
            """
            conn.query(user_query, {'user_id': user_id, 'name': name, 'email': email, 'password': password})

            relationship_query = """
            MATCH (u:User {user_id: $user_id})
            MERGE (l:Library {name: "My Library"})
            MERGE (u)-[:CAN_ACCESS]->(l)
            """
            conn.query(relationship_query, {'user_id': user_id})

        finally:
            conn.close()

        return JsonResponse({'success': True, 'message': 'User registered successfully'})

    # If the request method is not GET or POST, return an error
    return HttpResponse("Method not allowed", status=405)



from passlib.hash import bcrypt

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from django.views.decorators.csrf import csrf_exempt

# Initialize the logger at the top of the file
logger = logging.getLogger(__name__)

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json

# Initialize logger
logger = logging.getLogger(__name__)

@csrf_exempt
def login(request):
    try:
        if request.method == "GET":
            # Render the login page for GET requests
            logger.info("Rendering login page")
            return render(request, "login.html")  # Ensure "login.html" exists in your templates folder

        elif request.method == "POST":
            # Process the login form for POST requests
            logger.info("Login POST request received")
            try:
                data = json.loads(request.body)
                email = data.get('email')
                password = data.get('password')

                if not email or not password:
                    return JsonResponse({'success': False, 'error': 'Email and password are required'}, status=400)

                # Authenticate the user using Neo4j
                conn = Neo4jConnection()
                query = """
                MATCH (u:User {email: $email})
                RETURN u.password AS stored_password, u.user_id AS user_id
                """
                result = conn.query(query, {'email': email})
                conn.close()

                if result:
                    stored_password = result[0].get('stored_password')
                    user_id = result[0].get('user_id')

                    # Password validation (add hashing if required)
                    if password == stored_password:
                        request.session['user_id'] = user_id  # Save user ID in session
                        return JsonResponse({'success': True, 'message': 'Login successful'})
                    else:
                        return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)
                else:
                    return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)

            except json.JSONDecodeError:
                logger.error("Invalid JSON in request body")
                return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)

        else:
            # Return a 405 response for unsupported methods
            logger.warning("Invalid request method")
            return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    except Exception as e:
        logger.error(f"Unexpected error in login view: {e}")
        return JsonResponse({'success': False, 'error': 'An unexpected error occurred'}, status=500)




@csrf_exempt
def update_user_progress(request):
    if request.method == "POST":
        try:
            # Parse the request data
            data = json.loads(request.body)
            user_id = data.get("user_id")
            page_id = data.get("page_id")
            completed = data.get("completed")

            # Validate the input
            if not user_id or not page_id:
                return JsonResponse({"success": False, "error": "Missing user_id or page_id"}, status=400)

            # Update the user's progress in Neo4j
            conn = Neo4jConnection()
            query = """
            MATCH (u:User {user_id: $user_id}), (p:Page {id: $page_id})
            MERGE (u)-[r:PROGRESS]->(p)
            SET r.completed = $completed
            """
            conn.query(query, {"user_id": user_id, "page_id": page_id, "completed": completed})
            conn.close()

            return JsonResponse({"success": True, "message": "User progress updated successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)
    

def home(request):
    user_id = request.session.get('user_id')  # Retrieve user ID from session

    if not user_id:
        # If the user is not logged in, redirect to the login page
        return redirect('/login/')

    # Retrieve user name from Neo4j using the user ID
    conn = Neo4jConnection()
    user_query = """
    MATCH (u:User {user_id: $user_id})
    RETURN u.name AS name
    """
    user_result = conn.query(user_query, {'user_id': user_id})
    user_name = user_result[0]['name'] if user_result else 'User'
    
    # Query to fetch book titles and book_number
    query = """
    MATCH (b:Book)
    RETURN b.book_number AS book_number, b.title AS title
    """
    books = conn.query(query)
    conn.close()

    # Convert book_number to integer if it's returned as a float
    for book in books:
        book['book_number'] = int(book['book_number'])

    # Pass the user's name and books to the template
    return render(request, "home.html", {'user_name': user_name, 'books': books})



from django.http import JsonResponse
from .neo4j import Neo4jConnection

def get_book_progress(request, book_number):
    user_id = request.session.get('user_id')  # Assuming the user is logged in and session-managed
    if not user_id:
        return JsonResponse({"success": False, "error": "User not logged in"}, status=401)

    conn = Neo4jConnection()
    try:
        # Query to get completed pages for the user in the specified book
        query = """
        MATCH (u:User {user_id: $user_id})-[:PROGRESS {completed: true}]->(p:Page)<-[:UNIT_CONTAINS_PAGE]-(unit:Unit)<-[:BOOK_CONTAINS_UNIT]-(b:Book {book_number: $book_number})
        WITH count(p) AS completed_pages
        MATCH (b:Book {book_number: $book_number})-[:BOOK_CONTAINS_UNIT]->(:Unit)-[:UNIT_CONTAINS_PAGE]->(p:Page)
        RETURN count(p) AS total_pages, completed_pages
        """
        result = conn.query(query, {"user_id": user_id, "book_number": book_number})
        conn.close()

        if result:
            total_pages = result[0]["total_pages"]
            completed_pages = result[0]["completed_pages"]
            progress_percentage = (completed_pages / total_pages) * 100 if total_pages > 0 else 0

            return JsonResponse({
                "success": True,
                "total_pages": total_pages,
                "completed_pages": completed_pages,
                "progress_percentage": progress_percentage
            })
        else:
            return JsonResponse({"success": False, "error": "No progress data found"}, status=404)
    except Exception as e:
        conn.close()
        return JsonResponse({"success": False, "error": str(e)}, status=500)



def unitview(request, book_number):
    user_id = request.session.get('user_id')  # Assuming the user is logged in and session-managed

    if not user_id:
        return JsonResponse({"success": False, "error": "User not logged in"}, status=401)

    conn = Neo4jConnection()
    
    # Fetch book data
    book_query = """
    MATCH (b:Book {book_number: $book_number})-[:BOOK_CONTAINS_UNIT]->(u:Unit)-[:UNIT_CONTAINS_PAGE]->(p:Page)
    RETURN b.title AS title, 
           b.author AS author, 
           b.cover_image AS cover_image, 
           u.id AS unit, 
           u.title AS unit_title, 
           collect({id: p.id, content: p.content}) AS pages, 
           u.completed AS completed
    ORDER BY u.id
    """
    book_data = conn.query(book_query, {'book_number': book_number})
    
    # Fetch user's progress data
    progress_query = """
    MATCH (u:User {user_id: $user_id})-[r:PROGRESS]->(p:Page)<-[:UNIT_CONTAINS_PAGE]-(unit:Unit)<-[:BOOK_CONTAINS_UNIT]-(b:Book {book_number: $book_number})
    RETURN p.id AS page_id, r.completed AS completed
    """
    progress_data = conn.query(progress_query, {'user_id': user_id, 'book_number': book_number})
    conn.close()

    # Convert progress data to a dictionary for easy lookup
    progress_dict = {progress['page_id']: progress['completed'] for progress in progress_data}

    if book_data:
        units = [
            {
                'unit': row.get('unit'),
                'unit_title': row.get('unit_title', 'Untitled Unit'),
                'pages': [
                    {
                        'id': page['id'],
                        'content': page['content'],
                        'completed': progress_dict.get(page['id'], False)  # Set completed status based on user progress
                    } for page in row.get('pages', [])
                ],
                'completed': row.get('completed', False),
            }
            for row in book_data
        ]

        total_pages = sum(len(unit['pages']) for unit in units)

        context = {
            'user_id': user_id,
            'book_title': book_data[0]['title'],
            'book_author': book_data[0]['author'],
            'cover_image': book_data[0].get('cover_image', '/static/images/default_cover.jpg'),
            'units': units,
            'total_pages': total_pages
        }
    else:
        context = {
            'user_id': user_id,
            'book_title': "Unknown Title",
            'book_author': "Unknown Author",
            'cover_image': '/static/images/default_cover.jpg',
            'units': [],
            'total_pages': 0
        }

    return render(request, "unitview.html", context)





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .neo4j import Neo4jConnection  # Ensure this import is correct

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def toggle_page_completed_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            page_id = data.get('page_id')
            completed = data.get('completed', False)

            if not user_id or not page_id:
                return JsonResponse({'success': False, 'error': 'Missing user_id or page_id.'}, status=400)

            conn = Neo4jConnection()
            query = """
            MATCH (u:User {user_id: $user_id})-[r:PROGRESS]->(p:Page {id: $page_id})
            SET r.completed = $completed
            """
            conn.query(query, {'user_id': user_id, 'page_id': page_id, 'completed': completed})
            conn.close()

            return JsonResponse({'success': True, 'message': 'User progress updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
