from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def check_users(request):
    """Debug endpoint to check if users exist"""
    User = get_user_model()
    
    users = []
    for user in User.objects.all():
        users.append({
            'username': user.username,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })
    
    return JsonResponse({
        'total_users': User.objects.count(),
        'users': users,
        'admin_exists': User.objects.filter(username='admin').exists(),
        'user_exists': User.objects.filter(username='user').exists(),
    })
