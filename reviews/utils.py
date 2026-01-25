import os
import uuid


def ticket_image_upload_path(instance, filename):
    """
    Return a unique upload path for a ticket image.
    Generate a UUID-based filename and place it in the 'tickets' folder.
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('tickets', filename)
