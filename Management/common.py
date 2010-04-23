from datetime import datetime
import settings

def current_month():
    now = datetime.now()
    if now.day <= 22:
        now = datetime(now.month == 1 and now.year - 1 or now.year, 
                       now.month == 1 and 12 or now.month - 1, 
                       now.day)
    return now

def generate_unique_media_filename(ext):
    return settings.MEDIA_ROOT + 'temp/' + datetime.now().strftime('%Y%m%d%H%M%S') + '.' + ext

def clone(from_object, save):
    args = dict([(fld.name, getattr(from_object, fld.name)) 
                 for fld in from_object._meta.fields 
                 if fld is not from_object._meta.pk])
    if save:
        return from_object.__class__.objects.create(**args)
    else:
        new_object = from_object.__class__(**args)
        return new_object