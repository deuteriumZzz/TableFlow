from django.db import connection, OperationalError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    try:
        connection.ensure_connection()
        db_ok = True
    except OperationalError:
        db_ok = False

    http_status = 200 if db_ok else 503
    return Response(
        {'status': 'ok' if db_ok else 'degraded', 'db': db_ok},
        status=http_status,
    )
