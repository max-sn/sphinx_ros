import os
import rospkg
import subprocess
import catkin_pkg.package

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList

from ...util import split_pkg_object

from ..parsers.service_type import ServiceTypeParser


class RosAutoServiceDirective(Directive):

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'verbose': directives.flag
    }

    def run(self):
        source, _ = self.state_machine.get_source_and_line()
        str_list = ['.. ros:service:: {}'.format(self.arguments[0].strip())]
        str_list.append('')
        pkg, srv = split_pkg_object(self.arguments[0].strip(), 'srv')
        if not pkg:
            pkg = self.options.get(
                'package',
                self.state.document.settings.env.ref_context.get(
                    'ros:package'))

        parser = ServiceTypeParser(pkg=pkg, item=srv)
        srv_obj = parser.parse()
        if srv_obj.request.params:
            for par in srv_obj.request.params:
                str_list.append('  :req_param {}: {}'.format(par.name,
                                                             par.description))
                if par.type.endswith('[]'):
                    type_desc = ':ros:msg:`{} <{}>`'.format(par.type,
                                                            par.type[:-2])
                else:
                    type_desc = ':ros:msg:`{}`'.format(par.type)
                str_list.append('  :req_paramtype {}: {}'.format(par.name,
                                                                 type_desc))
        else:
            str_list.append('  :Request parameters: *- None -*')
        str_list.append('')
        if srv_obj.response.params:
            for par in srv_obj.response.params:
                str_list.append('  :resp_param {}: {}'.format(par.name,
                                                              par.description))
                if par.type.endswith('[]'):
                    type_desc = ':ros:msg:`{} <{}>`'.format(par.type,
                                                            par.type[:-2])
                else:
                    type_desc = ':ros:msg:`{}`'.format(par.type)
                str_list.append('  :resp_paramtype {}: {}'.format(par.name,
                                                                  type_desc))
        else:
            str_list.append('  :Response parameters: *- None -*')
        str_list.append('')
        for line in srv_obj.request.description:
            str_list.append('  ' + line)
            str_list.append('')
        for line in srv_obj.response.description:
            str_list.append('  ' + line)
            str_list.append('')
        if 'verbose' in self.options:
            for line in str_list:
                print(line)
        rst = ViewList(str_list, source=source)
        ret = nodes.paragraph()
        self.state.nested_parse(rst, 0, ret)
        return ret.children
