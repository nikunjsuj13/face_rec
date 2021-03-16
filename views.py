from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from models import detected_faces
from flask_appbuilder.widgets import ListThumbnail
class PersonModelView(ModelView):
    datamodel = SQLAInterface(detected_faces)

    list_widget = ListThumbnail

    label_columns = {'name':'Name','photo':'Photo','photo_img':'Photo', 'photo_img_thumbnail':'Photo'}
    list_columns = ['photo_img_thumbnail', 'name']
    show_columns = ['photo_img','name']