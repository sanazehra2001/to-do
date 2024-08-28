
import time
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

class QueryCountMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        self.get_response = get_response
        
    def process_request(self, request):
        # Called on each request, beforeDjango decides which view to execute 
        self.queries_before = len(connection.queries)
        self.start_time = time.time()
    
    def process_response(self, request, response):
        # Called on all responses before they are returned to the browser

        queries_after = len(connection.queries)
        queries_count = queries_after - self.queries_before

        # Calculate the total time taken for the request
        total_time = time.time() - self.start_time

        # Add the query count and execution time to the response headers
        response["X-Query-Count"] = str(queries_count)
        response["X-Total-Time"] = f"{total_time:.2f}s"

        return response