{
    'name': 'Smart Reorder Forecast',
    'version': '1.0',
    'summary': 'Forecast product stock depletion based on historical usage',
    'description': 'Adds average usage and stock-out prediction for smarter reordering decisions.',
    'author': 'jaynatz',
    'category': 'Inventory',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/product_kanban_forecast.xml',
        'views/forecast_dashboard_views.xml',
    ],
    'installable': True,
    'application': False,
}
