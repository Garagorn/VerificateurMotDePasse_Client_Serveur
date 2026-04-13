import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
import os
import sys

"""
Configuration du systeme de logging pour le serveur
"""
def setup_logger():

    #Dossier log
    if not os.path.exists('logs'):
        os.makedirs('logs')

    #Configuration
    logger = logging.getLogger('auth_server')
    logger.setLevel(logging.DEBUG)
    
    if logger.hasHandlers():
        logger.handlers.clear()

    # Format
    format_log = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = jsonlogger.JsonFormatter(
        format_log,
        rename_fields={
            "asctime":"timestamp",
            "levelname":'level',
            "name":"logger_name"
        }
    )

    # Handler pour rotation
    file_handler = RotatingFileHandler(
        'logs/server.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    #Handler pour console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger