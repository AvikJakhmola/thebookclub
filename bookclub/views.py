from django.shortcuts import render
from django.http import JsonResponse
from .neo4j import Neo4jConnection  # Ensure the correct import path
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

def home(request):
    conn = Neo4jConnection()
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

    return render(request, "home.html", {'books': books})

def page_detail(request, page_id):
    conn = Neo4jConnection()
    query = """
    MATCH (p:Page {id: $page_id})
    RETURN p.id AS id, p.content AS content
    """
    page_data = conn.query(query, {'page_id': page_id})
    conn.close()

    if page_data:
        page = page_data[0]  # Extract the first (and only) result
        return render(request, "page_detail.html", {'page': page})
    else:
        return render(request, "404.html", status=404)



def unitview(request, book_number):
    conn = Neo4jConnection()
    query = """
    MATCH (b:Book {book_number: $book_number})-[:BOOK_CONTAINS_UNIT]->(u:Unit)-[:UNIT_CONTAINS_PAGE]->(p:Page)
    RETURN b.title AS title, 
           b.author AS author, 
           b.cover_image AS cover_image, 
           u.id AS unit, 
           u.title AS unit_title, 
           collect({id: p.id, content: p.content, completed: p.completed}) AS pages, 
           u.completed AS completed
    ORDER BY u.id
    """
    book_data = conn.query(query, {'book_number': book_number})
    conn.close()

    if book_data:
        book_title = book_data[0]['title']
        book_author = book_data[0]['author']
        cover_image = book_data[0].get('cover_image', '/static/images/default_cover.jpg')
        units = [
            {
                'unit': row.get('unit'),
                'unit_title': row.get('unit_title', 'Untitled Unit'),
                'pages': row.get('pages', []),  # Ensure pages is a list
                'completed': row.get('completed', False),
            }
            for row in book_data
        ]

        total_pages = sum(len(unit['pages']) for unit in units)
    else:
        book_title = "Unknown Title"
        book_author = "Unknown Author"
        cover_image = '/static/images/default_cover.jpg'
        units = []
        total_pages = 0

    return render(request, "unitview.html", {
        'book_title': book_title,
        'book_author': book_author,
        'cover_image': cover_image,
        'units': units,
        'total_pages': total_pages,
    })




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .neo4j import Neo4jConnection  # Ensure this import is correct

@csrf_exempt
def toggle_page_completed_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            page_id = data.get('page_id')
            completed = data.get('completed', False)

            if not page_id:
                return JsonResponse({'success': False, 'error': 'Page ID is missing.'}, status=400)

            conn = Neo4jConnection()
            query = """
            MATCH (p:Page {id: $page_id})
            SET p.completed = $completed
            RETURN p.completed AS new_status
            """
            result = conn.query(query, {'page_id': page_id, 'completed': completed})
            conn.close()

            if result:
                return JsonResponse({'success': True, 'completed': result[0]['new_status']})
            else:
                return JsonResponse({'success': False, 'error': 'Failed to update the page.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
    

    