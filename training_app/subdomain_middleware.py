"""
Subdomain middleware for region-based routing
Allows accessing regions via subdomains:
- quebec.rtmtoyota.ca
- central.rtmtoyota.ca  
- pacific.rtmtoyota.ca
- prairie.rtmtoyota.ca
- atlantic.rtmtoyota.ca
"""
from django.http import Http404
from django.shortcuts import redirect
from .models import TrainingPage


class SubdomainRoutingMiddleware:
    """
    Middleware to handle subdomain-based region routing
    
    Examples:
    - quebec.rtmtoyota.ca → Shows Quebec training page
    - central.rtmtoyota.ca → Shows Central training page
    
    Also preserves path-based routing:
    - rtmtoyota.ca/quebec/ → Shows Quebec training page
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.valid_regions = ['quebec', 'central', 'pacific', 'prairie', 'atlantic']
        
    def __call__(self, request):
        # Get the host (e.g., quebec.rtmtoyota.ca or rtmtoyota.ca)
        host = request.get_host().split(':')[0]  # Remove port if present
        
        # Extract subdomain
        parts = host.split('.')
        
        # Check if we have a subdomain (more than 2 parts: subdomain.domain.tld)
        if len(parts) >= 3:
            subdomain = parts[0]
            
            # Check if subdomain matches a valid region
            if subdomain in self.valid_regions:
                # Store the region in the request for easy access
                request.subdomain_region = subdomain
                
                # If accessing the root path with a region subdomain,
                # redirect to the region view
                if request.path == '/' or request.path == '':
                    # Redirect to the region page view
                    return redirect(f'/{subdomain}/')
        
        # Continue with normal request processing
        response = self.get_response(request)
        return response

