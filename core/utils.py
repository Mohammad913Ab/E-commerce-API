def product_image_upload_to(instance, filename):
    """
    Returns path: product_images/<product-slug>/<original-filename>
    """
    return f"product_images/{instance.product.slug}/{filename}"
