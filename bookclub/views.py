from django.shortcuts import render
from django.http import HttpResponse
from .neo4j import Neo4jConnection  # Ensure the correct import path based on where your neo4j.py file is

# Create your views here.
def home(request):
    return render(request, "home.html")
def deep_learning(request):
    # Initialize Neo4j connection
    conn = Neo4jConnection()

    # Query to fetch book title, author, unit titles, and number of pages per unit
    query = """
    MATCH (b:Book)-[:BOOK_CONTAINS_UNIT]->(u:Unit)-[:UNIT_CONTAINS_PAGE]->(p:Page)
    RETURN b.title AS title, b.author AS author, u.unit_number AS unit, u.title AS unit_title, count(p) AS pages
    ORDER BY u.unit_number
    """

    # Run the query
    book_data = conn.query(query)
    conn.close()

    # Extract book title, author, and unit data
    if book_data:
        book_title = book_data[0]['title']
        book_author = book_data[0]['author']

        # Create a list of units with their respective page counts and titles
        units = [{'unit': row['unit'], 'unit_title': row['unit_title'], 'pages': row['pages']} for row in book_data]
        total_pages = sum(unit['pages'] for unit in units)

    else:
        book_title = 'Unknown Title'
        book_author = 'Unknown Author'
        units = []
        total_pages = 0

    # Pass the book title, author, and units to the template context
    return render(request, 'deeplearning.html', {
        'book_title': book_title,
        'book_author': book_author,
        'units': units,
        'total_pages': total_pages
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Allows bypassing CSRF check for simplicity; use CSRF tokens in production
def toggle_completed_status(request):
    if request.method == "POST":
        try:
            # Parse JSON data from the request
            data = json.loads(request.body)
            unit_id = data.get('unit_id')
            completed = data.get('completed', False)

            # Update the completed status in Neo4j
            conn = Neo4jConnection()
            query = """
            MATCH (u:Unit {unit_number: $unit_id})
            SET u.completed = $completed
            RETURN u
            """
            conn.query(query, parameters={'unit_id': int(unit_id), 'completed': completed})
            conn.close()

            # Respond with success
            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error updating completed status: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})




