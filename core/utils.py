def product_image_upload_to(instance, filename):
    """
    Returns path: product_images/<product-slug>/<original-filename>
    """
    return f"product_images/{instance.product.slug}/{filename}"

def get_client_ip(request):
    """
    Retrieve the client's IP address from the Django request object.
    
    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        str: The IP address of the client.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
