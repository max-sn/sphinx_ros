"""
``directives`` module
=====================


"""

import re
import sphinx

from docutils import nodes
from docutils.parsers.rst import directives, Directive
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.util.docfields import Field, TypedField


ros_sig_re = re.compile(
    r'''^((?:[^\.]*\.)*?)         # package name
         (?:(msg|srv|action)\.)?  # object type
         (\w+) \s*?$              # thing name
     ''', re.VERBOSE)


def name_to_key(name):
    return unicode(name[0].upper())


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
        'package': directives.unchanged,
    }

    def get_signature_prefix(self, sig):
        """
        May return a prefix to put before the object name in the signature.
        """
        return ''

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
        m = ros_sig_re.match(sig)
        if m is None:
            raise ValueError
        name_prefix, obj_type, name = m.groups()
        name_prefix = name_prefix.rstrip('.')

        pkgname = self.options.get(
            'package', self.env.ref_context.get('ros:package'))
        if not obj_type:
            obj_type = self.get_object_type_prefix()
        if name_prefix and name_prefix.startswith(pkgname):
            fullname = '.'.join([name_prefix, obj_type, name])
            name_prefix = name_prefix[len(pkgname):].lstrip('.')
        elif name_prefix:
            fullname = '.'.join([pkgname, name_prefix, obj_type, name])
        else:
            fullname = '.'.join([pkgname, obj_type, name])

        signode['package'] = pkgname
        signode['fullname'] = fullname

        sig_prefix = self.get_signature_prefix(sig)
        if sig_prefix:
            signode += addnodes.desc_annotation(sig_prefix, sig_prefix)

        if name_prefix:
            signode += addnodes.desc_addname(name_prefix, name_prefix)
        elif self.env.config.ros_add_package_names:
            if pkgname:
                nodetext = pkgname + '.'
                if obj_type:
                    nodetext += obj_type + '.'
                signode += addnodes.desc_addname(nodetext, nodetext)

        signode += addnodes.desc_name(name, name)
        return fullname, name_prefix, obj_type

    def get_index_text(self, pkgname, name):
        """
        Return the text for the index entry of the object.
        """
        raise NotImplementedError('must be implemented in subclasses')

    def add_object_to_domain_data(self, fullname, obj_type):
        """
        Add the object to the object lists of the ROS domain data.
        """
        raise NotImplementedError('must be implemented in subclasses')

    def add_target_and_index(self, name, sig, signode):
        pkgname = self.options.get('package',
                                   self.env.ref_context.get('ros:package'))

        fullname = name[0]
        obj_type = name[2]
        # Note target
        if fullname not in self.state.document.ids:
            signode['names'].append(fullname)
            signode['ids'].append(fullname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)

            self.add_object_to_domain_data(fullname, obj_type)

            # objects = self.env.domaindata['ros']['objects']
            # if fullname in objects:
            #     self.state_machine.reporter.warning(
            #         'duplicate object description of %s, ' % fullname +
            #         'other instance in ' +
            #         self.env.doc2path(objects[fullname][0]) +
            #         ', use :noindex: for one of them',
            #         line=self.lineno)
            # objects[fullname] = (self.env.docname, self.objtype)

            indextext = self.get_index_text(pkgname, name)
            if sphinx.version_info[:2] >= (1, 4):
                entry = ('single', indextext, fullname, '',
                         name_to_key(name[0]))
            else:
                entry = ('single', indextext, fullname, '')
            if indextext:
                self.indexnode['entries'].append(entry)


class RosField(RosXRefMixin, Field):
    pass


class RosTypedField(RosXRefMixin, TypedField):
    pass


class RosType(RosObject):
    """
    Super class for messages, services, and actions.
    """

    def get_object_type_prefix(self):
        if self.objtype == 'message':
            return 'msg'
        elif self.objtype == 'service':
            return 'srv'
        elif self.objtype == 'action':
            return 'action'

    def get_signature_prefix(self, sig):
        return self.objtype + ' '

    def get_index_text(self, pkgname, name):
        fullname = name[0]
        obj_type = name[2]
        if pkgname:
            if fullname.startswith(pkgname):
                newname = re.sub(r'^' + pkgname + r'\.', '', fullname)
                if newname.startswith(obj_type):
                    newname = re.sub(r'^' + obj_type + r'\.', '', newname)
            return '{} ({} in package {})'.format(newname, self.objtype,
                                                  pkgname)
        else:
            return '{} ({})'.format(fullname, self.objtype)

    def add_object_to_domain_data(self, fullname, obj_type):
        objects = self.env.domaindata['ros']['objects']
        if fullname in objects:
            self.state_machine.reporter.warning(
                'duplicate object description of %s, ' % fullname +
                'other instance in ' +
                self.env.doc2path(objects[fullname][0]) +
                ', use :noindex: for one of them',
                line=self.lineno)
        objects[fullname] = (self.env.docname, self.objtype)


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
            # env.domaindata['ros']['packages'][pkgname] = \
            #     (env.docname, 'deprecated' in self.options)
            # env.domaindata['ros']['objects'][pkgname] = \
            #     (env.docname, 'package')
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


class RosMessageDirective(RosType):
    """
    Description of a ROS message type.
    """

    option_spec = {
        'noindex': directives.flag,
        'package': directives.unchanged,
        'deprecated': directives.flag,
    }
    # option_spec['deprecated'] = directives.flag

    doc_field_types = [
        RosTypedField('parameter',
                      label='Parameters',
                      names=('msg_param',),
                      typerolename='obj',
                      typenames=('msg_paramtype',),
                      can_collapse=True),
    ]

    def add_object_to_domain_data(self, fullname, obj_type):
        ros_domain = self.env.get_domain('ros')
        ros_domain.add_message(fullname, 'deprecated' in self.options)
