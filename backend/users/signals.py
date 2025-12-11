from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
    User = get_user_model()
    admin_user, created = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@example.com',
        'is_superuser': True,
        'is_staff': True,
        'is_active': True,
    })
    admin_user.set_password('admin123')
    admin_user.save()
