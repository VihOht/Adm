import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image

# Create your models here.


def user_profile_image_path(instance, filename):
    """Generate file path for user profile images"""
    # Get file extension
    ext = filename.split(".")[-1]
    # Create filename: user_id.ext
    filename = f"user_{instance.id}.{ext}"
    # Return path: media/profile_images/user_id.ext
    return os.path.join("profile_images", filename)


class User(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    profile_image = models.ImageField(
        upload_to=user_profile_image_path,
        null=True,
        blank=True,
        help_text="Upload a profile image (max 5MB, JPG/PNG)",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Resize image if it exists
        if self.profile_image:
            self.resize_image()

    def resize_image(self):
        """Resize profile image to 300x300 pixels"""
        if not self.profile_image or not hasattr(self.profile_image, "path"):
            return

        try:
            with Image.open(self.profile_image.path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                # Resize image to 300x300 (maintaining aspect ratio and cropping center)
                img = img.resize((300, 300), Image.Resampling.LANCZOS)

                # Save with optimized quality
                img.save(self.profile_image.path, "JPEG", quality=85, optimize=True)
        except Exception as e:
            # Log error but don't raise exception to prevent breaking user save
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error resizing profile image for user {self.pk}: {e}")

    def get_profile_image_url(self):
        """Get profile image URL or return default"""
        if self.profile_image and hasattr(self.profile_image, "url"):
            return self.profile_image.url
        return None

    def delete_profile_image(self):
        """Delete profile image file when removing"""
        if self.profile_image and hasattr(self.profile_image, "path"):
            if os.path.isfile(self.profile_image.path):
                os.remove(self.profile_image.path)
            self.profile_image = None
            self.save()
