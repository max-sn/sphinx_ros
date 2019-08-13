import os
import rospkg
import subprocess
import catkin_pkg.package

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList

from ...util import split_pkg_object

from ..parsers.action_type import ActionTypeParser


class RosAutoActionDirective(Directive):

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'verbose': directives.flag
    }

    def run(self):
        source, _ = self.state_machine.get_source_and_line()
        str_list = ['.. ros:action:: {}'.format(self.arguments[0].strip())]
        str_list.append('')
        pkg, act = split_pkg_object(self.arguments[0].strip(), 'msg')
        if not pkg:
            pkg = self.options.get(
                'package',
                self.state.document.settings.env.ref_context.get(
                    'ros:package'))

        parser = ActionTypeParser(pkg=pkg, item=act)
        act_obj = parser.parse()
        if act_obj.goal.params:
            for par in act_obj.goal.params:
                str_list.append('  :goal_param {}: {}'.format(par.name,
                                                              par.description))
                if par.type.endswith('[]'):
                    type_desc = ':ros:msg:`{} <{}>`'.format(par.type,
                                                            par.type[:-2])
                else:
                    type_desc = ':ros:msg:`{}`'.format(par.type)
                str_list.append('  :goal_paramtype {}: {}'.format(par.name,
                                                                  type_desc))
        else:
            str_list.append('  :Goal parameters: *- None -*')
        str_list.append('')
        if act_obj.result.params:
            for par in act_obj.result.params:
                str_list.append('  :result_param {}: {}'.format(
                    par.name, par.description))
                if par.type.endswith('[]'):
                    type_desc = ':ros:msg:`{} <{}>`'.format(par.type,
                                                            par.type[:-2])
                else:
                    type_desc = ':ros:msg:`{}`'.format(par.type)
                str_list.append('  :result_paramtype {}: {}'.format(par.name,
                                                                    type_desc))
        else:
            str_list.append('  :Result parameters: *- None -*')
        str_list.append('')
        if act_obj.feedback.params:
            for par in act_obj.feedback.params:
                str_list.append('  :feedback_param {}: {}'.format(
                    par.name, par.description))
                if par.type.endswith('[]'):
                    type_desc = ':ros:msg:`{} <{}>`'.format(par.type,
                                                            par.type[:-2])
                else:
                    type_desc = ':ros:msg:`{}`'.format(par.type)
                str_list.append('  :feedback_paramtype {}: {}'.format(
                    par.name, type_desc))
        else:
            str_list.append('  :Feedback parameters: *- None -*')
        str_list.append('')
        for line in act_obj.goal.description:
            str_list.append('  ' + line)
            str_list.append('')
        for line in act_obj.result.description:
            str_list.append('  ' + line)
            str_list.append('')
        for line in act_obj.feedback.description:
            str_list.append('  ' + line)
            str_list.append('')
        if 'verbose' in self.options:
            for line in str_list:
                print(line)
        rst = ViewList(str_list, source=source)
        ret = nodes.paragraph()
        self.state.nested_parse(rst, 0, ret)
        return ret.children
