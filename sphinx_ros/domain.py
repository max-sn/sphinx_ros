"""
``sphinx_ros.domain`` module
============================

This module defines the ROS domain. It defines three object types (messages,
services, and actions) and registers the roles and directives in the Sphinx
application.
"""

from six import iteritems
from docutils import nodes
from sphinx.domains import Domain, ObjType
from sphinx.util.nodes import make_refnode
from .xref_role import RosXRefRole
from .directives import RosPackageDirective, RosCurrentPackageDirective, \
    RosMessageDirective, RosActionDirective, RosServiceDirective
from .indices import RosPackageIndex, RosMessageIndex

from .autoros.directives import RosAutoActionDirective, \
    RosAutoMessageDirective, RosAutoServiceDirective, RosAutoPackageDirective


class RosDomain(Domain):
    """
    The actual domain class.
    """
    name = 'ros'
    label = 'ROS'
    object_types = {
        'message':   ObjType('message', 'msg', 'obj'),
        'service':   ObjType('service', 'srv', 'obj'),
        'action':    ObjType('action', 'action', 'obj')
    }
    roles = {
        'pkg': RosXRefRole(),
        'msg': RosXRefRole(),
        'srv': RosXRefRole(),
        'act': RosXRefRole()
    }
    directives = {
        'package':          RosPackageDirective,
        'currentpackage':   RosCurrentPackageDirective,
        'message':          RosMessageDirective,
        'service':          RosServiceDirective,
        'action':           RosActionDirective,
        'autopackage':      RosAutoPackageDirective,
        'automessage':      RosAutoMessageDirective,
        'autoservice':      RosAutoServiceDirective,
        'autoaction':       RosAutoActionDirective,
    }
    initial_data = {
        'objects': {},   # fullname -> docname, objtype
        'packages': {},  # name -> document name, anchor, priority, deprecated
        'messages': {},  # name -> document name, anchor, priority, deprecated
        'labels': {
            'ros-pkgindex': ('ros-pkgindex', '', 'Package Index'),
            'ros-msgindex': ('ros-msgindex', '', 'Message Type Index')
        },
        'anonlabels': {
            'ros-pkgindex': ('ros-pkgindex', ''),
            'ros-msgindex': ('ros-msgindex', '')
        }
    }
    indices = [
        RosPackageIndex,
        RosMessageIndex,
    ]

    def clear_doc(self, docname):
        for fullname, (fn, _l) in list(self.data['objects'].items()):
            if fn == docname:
                del self.data['objects'][fullname]
        # name -> document name, anchor, priority, deprecated
        for pkgname, (fn, _, _, _) in list(self.data['packages'].items()):
            if fn == docname:
                del self.data['packages'][pkgname]

    def find_obj(self, env, pkgname, name, type, searchmode=0):
        """
        Find a ROS object for ``name``, perhaps using ``pkgname``.
        """
        if name.endswith('()'):
            name = name[:-2]

        if not name:
            return []

        objects = self.data['objects']
        matches = []

        newname = None
        if searchmode == 1:
            if type is None:
                objtypes = list(self.object_types)
            else:
                objtypes = self.objtypes_for_role(type)
        else:
            # NOTE: searching for exact match, object type is not considered
            if name in objects:
                newname = name
            elif type == 'pkg':
                # only exact matches allowed for packages
                return []
            elif pkgname and pkgname + '.' + name in objects:
                newname = pkgname + '.' + name

        if newname is not None:
            matches.append((newname, objects[newname]))
        return matches

    def resolve_xref(self, env, fromdocname, builder, type, target, node,
                     contnode):
        pkgname = node.get('ros:package')
        searchmode = node.hasattr('refspecific') and 1 or 0

        matches = self.find_obj(env, pkgname, target, type, searchmode)

        if not matches:
            return None
        elif len(matches) > 1:
            env.warn_node(
                'more than one target found for cross-reference '
                '%r: %s' % (target, ', '.join(match[0] for match in matches)),
                node)
        name, obj = matches[0]

        if obj[1] == 'package':
            return self._make_package_refnode(builder, fromdocname, name,
                                              contnode)
        else:
            return make_refnode(builder, fromdocname, obj[0], name, contnode,
                                name)

    def resolve_any_xref(self, env, fromdocname, builder, target, node,
                         contnode):
        pkgname = node.get('ros:package')
        results = []

        # Always search in 'refspecific' mode with the :any: role
        matches = self.find_obj(env, pkgname, target, None, 1)
        for name, obj in matches:
            if obj[1] == 'package':
                results.append(('ros:pkg',
                               self._make_package_refnode(builder,
                                                          fromdocname,
                                                          name, contnode)))
            else:
                results.append(('ros:' + self.role_for_objtype(obj[1]),
                                make_refnode(builder, fromdocname, obj[0],
                                             name, contnode, name)))
        return results

    def _make_package_refnode(self, builder, fromdocname, name, contnode):
        # Get additional info for packages
        # name -> document name, anchor, priority, deprecated
        docname, anchor, _, deprecated = self.data['packages'][name]
        title = name
        if deprecated:
            title += ' (deprecated)'
        return make_refnode(builder, fromdocname, docname, anchor, contnode,
                            title)

    def get_objects(self):
        for pkgname, info in iteritems(self.data['packages']):
            yield (pkgname, pkgname, 'package', info[0],
                   'package-' + pkgname, 0)
        for refname, (docname, type) in iteritems(self.data['objects']):
            if type != 'package':
                yield (refname, refname, type, docname, refname, 1)

    def add_package(self, name, deprecated):
        """
        Adds a package to the domain data.

        :param str name: The name of the package
        :param bool deprecated: Indicates whether the package is deprecated.
        :return: The unique anchor of the package.
        :rtype: str
        """
        anchor = 'ros-pkg-{}'.format(name)
        # name -> document name, anchor, priority, deprecated
        self.data['packages'][name] = (self.env.docname, anchor, 0, deprecated)
        # make a duplicate entry in 'objects' to facilitate searching for the
        # package in RosDomain.find_obj()
        self.data['objects'][name] = (self.env.docname, 'package')
        return anchor

    def add_message(self, name, deprecated):
        # name -> document name, anchor, priority, deprecated
        self.data['messages'][name] = (self.env.docname, name, 0, deprecated)
        self.data['objects'][name] = (self.env.docname, 'message')
        return name
