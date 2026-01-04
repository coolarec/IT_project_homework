from .models import Test

def get_tests():
    return Test.objects.all()
