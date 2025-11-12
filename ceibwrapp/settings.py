# ceibwrapp settings

import os

SRC_FOLDER = os.path.dirname(os.path.abspath(__file__))
PROJECT_FOLDER = os.path.dirname(SRC_FOLDER)
CERDDI_FOLDER = os.path.join(os.path.dirname(PROJECT_FOLDER), 'cerddi/Uchelwyr')
# CERDDI_FOLDER = os.path.join(os.path.dirname(PROJECT_FOLDER), 'cerddi/test')
STATIC_FOLDER = os.path.join(SRC_FOLDER, 'static')
MEFUS_FOLDER = os.path.join(STATIC_FOLDER, 'mefus')
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
TMP_FOLDER = os.path.join(STATIC_FOLDER, 'tmp')
ALLOWED_EXTENSIONS = {'txt'}

