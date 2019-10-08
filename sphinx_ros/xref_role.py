"""
``sphinx_ros.xref_role`` module
===============================


"""
import re

from docutils import nodes
from sphinx.roles import XRefRole


class RosXRefRole(XRefRole):

    ros_msg_primitives = ['bool', 'int8', 'uint8', 'int16', 'uint16', 'int32',
                          'uint32', 'int64', 'uint64', 'float32', 'float64',
                          'string', 'time', 'duration']

    def process_link(self, env, refnode, has_explicit_title, title, target):
        refnode['ros:package'] = env.ref_context.get('ros:package')
        if not has_explicit_title:
            title = title.lstrip('.')    # only has a meaning for the target
            target = target.lstrip('~')  # only has a meaning for the title
            # if the first character is a tilde, don't display the package
            # part of the contents.
            if title.startswith('~'):
                title = title[1:]  # Not needed anymore
                title = re.split(r'[\./]', title)[-1]
        # if the first character is a dot, search more specific namespaces
        # first, else search builtins first
        if target.startswith('.'):
            target = target[1:]
            refnode['refspecific'] = True
        return title, target

    def result_nodes(self, document, env, node, is_ref):
        if node['reftype'] in ['msg', 'srv', 'action']:
            obj_type = node['reftype']
            title = node.astext()
            target = node['reftarget']

            # Check if target is an (fixed or variable length) array
            m = re.search(r'\[\d*\]$', target)
            if m:
                target = m.string[:m.start()]

            # If reference to a ros message, service, or action
            if target in self.ros_msg_primitives:
                # If the target is a ROS message primitive then don't add a
                # link.
                node = nodes.literal(title, title)
            elif target == "Header":
                # If the target is the message primitive "Header", then refer
                # to that documentation.
                target = 'http://docs.ros.org/' + \
                         env.config.ros_msg_reference_version + \
                         '/api/std_msgs/html/msg/Header.html'
                ref_node = nodes.reference()
                ref_node['refuri'] = target
                text_node = nodes.literal(title, title)
                text_node['classes'] = ['xref', 'ros', 'ros-' + obj_type]
                ref_node += text_node
                node = ref_node
            elif '/' in target:
                # If the target contains a forward slash, it is either a
                # reference to a standard ROS message type or a custom message
                # type.
                pkg, obj = target.split('/')
                ros_api_pkgs = env.config.ros_api_msg_packages
                if pkg in ros_api_pkgs:
                    # In the former case we link to the API documentation of
                    # ROS.
                    target = 'http://docs.ros.org/' + \
                        env.config.ros_msg_reference_version + \
                        '/api/{}/html/{}/{}.html'.format(pkg, obj_type, obj)
                    ref_node = nodes.reference()
                    ref_node['refuri'] = target
                    text_node = nodes.literal(title, title)
                    text_node['classes'] = ['xref', 'ros', 'ros-' + obj_type]
                    ref_node += text_node
                    node = ref_node
                else:
                    # In the latter case we change the link to the unique
                    # 'fullname' of the described object.
                    node['reftarget'] = '.'.join([pkg, node['reftype'], obj])

        return [node], []
