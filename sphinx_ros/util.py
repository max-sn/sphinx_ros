def name_to_key(name):
    return unicode(name[0].upper())


def split_pkg_object(signature, obj_type):
    try:
        pkg, object_ = signature.split('.' + obj_type + '.')
    except ValueError:
        try:
            pkg, object_ = signature.split('/')
        except ValueError:
            pkg = ''
            object_ = signature
    return pkg, object_
