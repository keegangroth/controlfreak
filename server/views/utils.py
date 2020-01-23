from django.http import HttpResponse, JsonResponse

from django.db import connection
from django.db.migrations.executor import MigrationExecutor

def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def health(request):
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    db = { 'name': connection.settings_dict['NAME'],
           'engine': connection.settings_dict['ENGINE'],
           'pending_migrations': [p[0].name for p in plan] }
    status = 503 if plan else 200
    return JsonResponse({'db': db}, status=status)
