import logging

from jenkinsapi.view import View
from jenkinsapi.jenkins import Jenkins

log_level = getattr(logging, 'DEBUG')
logging.basicConfig(level=log_level)
logger = logging.getLogger()

jenkins_url = "http://192.168.1.64:8080/"
api = Jenkins(jenkins_url)

# Create ListView in main view
logger.info('Attempting to create new view')
new_view = api.create_view('SimpleListView')
logger.info('new_view is %s' % new_view)
if new_view is None:
    logger.error('View was not created')
else:
    logger.info('View has been created')

logger.info('Attempting to create view that already exists')
if not api.create_view('SimpleListView'):
    logger.info('View was not created')
else:
    logger.error('View has been created')

logger.info('Attempting to delete view that already exists')
if not api.delete_view('SimpleListView'):
    logger.error('View was not deleted')
else:
    logger.info('View has been deleted')

logger.info('Attempting to delete view that does not exist')
if api.delete_view('SimpleListView'):
    logger.error('View has been deleted')
else:
    logger.info('View was not deleted')
