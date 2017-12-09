import os
import logging


logging.basicConfig(
    format='%(module)s.%(funcName)s %(levelname)s: %(message)s',
    level=logging.INFO
)

level = logging.WARNING if 'LOG_LEVEL' not in os.environ \
    else os.environ['LOG_LEVEL'].upper().strip()

modules = [
    'requests.packages.urllib3.connectionpool',
    'requests',
    'urllib3',
    'urllib3.connectionpool'
]

for module_name in modules:
    logger = logging.getLogger(module_name)
    logger.setLevel(level)
