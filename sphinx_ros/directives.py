"""
``sphinx_ros.directives`` module
================================


"""

import re
import sphinx

from docutils import nodes
from docutils.parsers.rst import directives, Directive
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.util.docfields import Field, TypedField

from .util import name_to_key, split_pkg_object


ros_sig_re = re.compile(
    r'''^((?:[^\.]*\.)*?)         # package name
         (?:(msg|srv|action)\.)?  # object type
         (\w+) \s*?$              # thing name
     ''', re.VERBOSE)


# This override allows our inline type specifiers to behave like :class: link
# when it comes to handling "." and "~" prefixes.
class RosXRefMixin(object):
    def make_xref(self, rolename, domain, target, innernode=nodes.emphasis,
                  contnode=None, env=None):
        if sphinx.version_info[:2] >= (1, 5):
            result = super(RosXRefMixin, self).make_xref(rolename, domain,
                                                         target, innernode,
                                                         contnode, env)
        else:
            result = super(RosXRefMixin, self).make_xref(rolename, domain,
                                                         target, innernode,
                                                         contnode)
        result['refspecific'] = True
        if target.startswith(('.', '~')):
            prefix, result['reftarget'] = target[0], target[1:]
            if prefix == '.':
                text = target[1:]
            elif prefix == '~':
                # text = target.split('.')[-1]
                text = re.split(r'[\./]', target)[-1]
            for node in result.traverse(nodes.Text):
                node.parent[node.parent.index(node)] = nodes.Text(text)
                break
        return result


class RosObject(ObjectDescription):
    """
    Description of a general ROS object.
    """
    option_spec = {
        'noindex': directives.flag,
        'deprecated': directives.flag
    }

    def get_signature_prefix(self, sig):
        """
        Return a prefix to put before the object name in the signature.
        """
        return self.objtype + ' '

    def get_object_type_prefix(self):
        """
        May return an optional name prefix that defines object type, e.g.
        'msg' or 'srv'.
        """
        return ''

    def handle_signature(self, sig, signode):
        """
        Transform a ROS signature into rST nodes.

        Return (fully qualified name of the thing, package name if any).

        If inside a package, the current package name is handled intelligently:
        * it is stripped from the displayed name if present
        * it is added to the full name (return value) if not present
        """
        pkg, name = split_pkg_object(sig, self.get_object_type_prefix())
        env_pkg = self.options.get('package',
                                   self.env.ref_context.get('ros:package'))
        if not pkg == env_pkg:
            # TODO: issue warning that object is in wrong package
            pass

        pkg_name = pkg and pkg or env_pkg

        name_prefix = '.'.join([pkg_name, self.get_object_type_prefix(),
                                ''])
        fullname = name_prefix + name

        signode['package'] = pkg_name
        signode['fullname'] = fullname

        sig_prefix = self.get_signature_prefix(sig)
        signode += addnodes.desc_annotation(sig_prefix, sig_prefix)
        if self.env.config.ros_add_package_names:
            signode += addnodes.desc_addname(pkg_name + '/', pkg_name + '/')
        signode += addnodes.desc_name(name, name)
        return fullname, name_prefix, self.objtype, name

    def get_index_text(self, pkgname, name):
        """
        Return the text for the index entry of the object.
        """
        fullname = name[0]
        name_prefix = name[1]
        short_name = name[3]
        if pkgname:
            text = '{} ({} in package {})'.format(short_name, self.objtype,
                                                  pkgname)
        else:
            text = '{} ({})'.format(fullname, self.objtype)
        return text

    def add_object_to_domain_data(self, fullname, obj_type):
        """
        Add the object to the object lists of the ROS domain data.
        """
        objects = self.env.domaindata['ros']['objects']
        if fullname in objects:
            self.state_machine.reporter.warning(
                'duplicate object description of %s, ' % fullname +
                'other instance in ' +
                self.env.doc2path(objects[fullname][0]) +
                ', use :noindex: for one of them',
                line=self.lineno)
        objects[fullname] = (self.env.docname, self.objtype)

    def add_target_and_index(self, name, sig, signode):
        pkgname = self.options.get('package',
                                   self.env.ref_context.get('ros:package'))

        fullname = name[0]
        obj_type = name[2]
        short_name = name[3]
        # Note target
        if fullname not in self.state.document.ids:
            signode['names'].append(fullname)
            signode['ids'].append(fullname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)

            self.add_object_to_domain_data(fullname, obj_type)

            indextext = self.get_index_text(pkgname, name)
            if sphinx.version_info[:2] >= (1, 4):
                entry = [('single', indextext, short_name, '',
                         name_to_key(short_name[0]))]
            else:
                entry = [('single', indextext, short_name, '')]
            if indextext:
                self.indexnode['entries'] += entry


class RosField(RosXRefMixin, Field):
    pass


class RosTypedField(RosXRefMixin, TypedField):
    pass


class RosType(RosObject):
    """
    Super class for messages, services, and actions.

    #TODO A lot of methods should be moved to RosObject, to simplify. RegEx in 
        RosObject is not needed.
    """
    pass


class RosCurrentPackageDirective(Directive):
    """
    This directive is just to tell Sphinx that we're documenting stuff in this
    package, but links to this package will not lead here.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env
        pkgname = self.arguments[0].strip()
        if pkgname == 'None':
            env.ref_context.pop('ros:package', None)
        else:
            env.ref_context['ros:package'] = pkgname
        return []


class RosPackageDirective(Directive):
    """
    Directive to mark description of a new package.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'noindex': directives.flag,
        'deprecated': directives.flag
    }

    def run(self):
        env = self.state.document.settings.env
        pkgname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.ref_context['ros:package'] = pkgname
        ret = []
        if not noindex:
            ros_domain = env.get_domain('ros')
            anchor = ros_domain.add_package(pkgname,
                                            'deprecated' in self.options)
            targetnode = nodes.target('', '', ids=[anchor])
            self.state.document.note_explicit_target(targetnode)
            ret.append(targetnode)
            indextext = '{} (package)'.format(pkgname)
            if sphinx.version_info[:2] >= (1, 4):
                entry = ('single', indextext, anchor, '',
                         name_to_key(pkgname))
            else:
                entry = ('single', indextext, anchor, '')

            inode = addnodes.index(entries=[entry])
            ret.append(inode)
        return ret


class RosActionDirective(RosType):
    """
    Description of a ROS action type.
    """

    doc_field_types = [
        RosTypedField('goal_parameter',
                      label='Goal parameters',
                      names=('goal_param',),
                      typerolename='obj',
                      typenames=('goal_paramtype',),
                      can_collapse=True),
        RosTypedField('result_parameter',
                      label='Result parameters',
                      names=('result_param',),
                      typerolename='obj',
                      typenames=('result_paramtype',),
                      can_collapse=True),
        RosTypedField('feedback_parameter',
                      label='Feedback parameters',
                      names=('feedback_param',),
                      typerolename='obj',
                      typenames=('feedback_paramtype',),
                      can_collapse=True)
    ]

    def get_object_type_prefix(self):
        return 'action'


class RosServiceDirective(RosType):
    """
    Description of a ROS service type.
    """

    doc_field_types = [
        RosTypedField('req_parameter',
                      label='Request parameters',
                      names=('req_param',),
                      typerolename='obj',
                      typenames=('req_paramtype',),
                      can_collapse=True),
        RosTypedField('resp_parameter',
                      label='Response parameters',
                      names=('resp_param',),
                      typerolename='obj',
                      typenames=('resp_paramtype',),
                      can_collapse=True)
    ]

    def get_object_type_prefix(self):
        return 'srv'


class RosMessageDirective(RosType):
    """
    Description of a ROS message type.
    """

    doc_field_types = [
        RosTypedField('parameter',
                      label='Parameters',
                      names=('msg_param',),
                      typerolename='obj',
                      typenames=('msg_paramtype',),
                      can_collapse=True),
    ]

    def get_object_type_prefix(self):
        return 'msg'

    def add_object_to_domain_data(self, fullname, obj_type):
        super(RosMessageDirective, self).add_object_to_domain_data(fullname,
                                                                   obj_type)
        ros_domain = self.env.get_domain('ros')
        ros_domain.add_message(fullname, 'deprecated' in self.options)


class RosNodeDirective(RosObject):
    """
    Description of a ROS node.
    """

    doc_field_types = [
        RosTypedField('publisher',
                      label='Publishers',
                      names=('publisher',),
                      typerolename='obj',
                      typenames=('publisher_msgtype',),
                      can_collapse=True),
        RosTypedField('subscriber',
                      label='Subscribers',
                      names=('subscriber',),
                      typerolename='ros:msg',
                      typenames=('subscriber_msgtype',),
                      can_collapse=True),
        RosTypedField('service',
                      label='Services',
                      names=('service',),
                      typerolename='ros:srv',
                      typenames=('service_srvtype',),
                      can_collapse=True)
    ]

    def get_object_type_prefix(self):
        return 'node'

    def add_object_to_domain_data(self, fullname, obj_type):
        super(RosNodeDirective, self).add_object_to_domain_data(fullname,
                                                                obj_type)
        ros_domain = self.env.get_domain('ros')
        ros_domain.add_node(fullname, 'deprecated' in self.options)
