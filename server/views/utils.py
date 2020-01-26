'''View for utility apis like /health'''

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
    '''Trivial index that just returns some static info'''
    return render(request, 'controlfreak/index.html')

def health(request):
    '''Health route suitable for a load balancer'''
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    db_info = {'name': connection.settings_dict['NAME'],
               'engine': connection.settings_dict['ENGINE'],
               'pending_migrations': bool(plan)}
    status = 503 if plan else 200
    return JsonResponse({'db': db_info}, status=status)
