import os
import glob
import rospkg
import subprocess
import catkin_pkg.package

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList

from sphinx.util.nodes import nested_parse_with_titles


HEADING_PYTHON_CONV = {
    'part':          '#',
    'chapter':       '*',
    'section':       '=',
    'subsection':    '-',
    'subsubsection': '^',
    'paragraph':     '"'}

HEADING_DOCUTILS_CONV = {
    'part':          '=',
    'chapter':       '-',
    'section':       '=',
    'subsection':    '-',
    'subsubsection': '`',
    'paragraph':     '"'}

PKG_DEPENDS = {
    'build_depends':            (':Build:',),
    'buildtool_depends':        (':Build tool:',),
    'build_export_depends':     (':Build export:',),
    'buildtool_export_depends': (':Build tool export:',),
    'exec_depends':             (':Execution:',),
    'test_depends':             (':Test:',),
    'doc_depends':              (':Documentation:',),
    'group_depends':            (':Group:',)}


class RosAutoPackageDirective(Directive):

    # USE_ROSMSG_CLI = True
    USE_ROSMSG_CLI = False

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        'verbose': directives.flag}

    def run(self):
        source, line = self.state_machine.get_source_and_line()
        str_list = self.auto_package(self.arguments[0].strip())
        rst = ViewList(str_list, source=source)
        ret = nodes.paragraph()
        nested_parse_with_titles(self.state, rst, ret)
        return ret.children

    def get_msgs(self, pkg):
        if self.USE_ROSMSG_CLI:
            msgs = subprocess.check_output(['rosmsg', 'package', pkg.name]).\
                strip().split('\n')
            if msgs == ['']:
                return None
            else:
                return msgs
        else:
            return [pkg.name + '/' + os.path.splitext(os.path.basename(msg))[0]
                    for msg in glob.glob(self.pkg_path + '/msg/*.msg')]

    def get_srvs(self, pkg):
        if self.USE_ROSMSG_CLI:
            srvs = subprocess.check_output(['rossrv', 'package', pkg.name]).\
                strip().split('\n')
            if srvs == ['']:
                return None
            else:
                return srvs
        else:
            return [pkg.name + '/' + os.path.splitext(os.path.basename(srv))[0]
                    for srv in glob.glob(self.pkg_path + '/srv/*.srv')]

    def get_acts(self, pkg):
        return [pkg.name + '/' + os.path.splitext(os.path.basename(action))[0]
                for action in glob.glob(self.pkg_path + '/action/*.action')]

    def make_literalincluce(self, fn, language='python'):
        ret = []
        source, _ = self.state_machine.get_source_and_line()
        path = os.path.relpath(self.pkg_path, start=os.path.dirname(source))
        ret.append('.. literalinclude:: {}/{}'.format(path, fn))
        ret.append('  :language: {}'.format(language))
        ret.append('  :linenos:')
        ret.append('')
        return ret

    def make_toc(self, depth=None):
        ret = []
        ret.append('.. contents::')
        ret.append('  :local:')
        if depth is not None:
            ret.append('  :depth: {}'.format(depth))
        ret.append('')
        return ret

    def make_heading(self, text, level, convention=HEADING_PYTHON_CONV):
        ret = []
        if level == 0 or level == 'part':
            return self._make_heading(text, convention['part'], overline=True)
        elif level == 1 or level == 'chapter':
            return self._make_heading(text, convention['chapter'], overline=True)
        elif level == 2 or level == 'section':
            return self._make_heading(text, convention['section'])
        elif level == 3 or level == 'subsection':
            return self._make_heading(text, convention['subsection'])
        elif level == 4 or level == 'subsubsection':
            return self._make_heading(text, convention['subsubsection'])
        elif level == 5 or level == 'paragraph':
            return self._make_heading(text, convention['paragraph'])

    def _make_heading(self, text, char, overline=False):
        ret = []
        if overline:
            ret.append('')
            ret.append(char * len(text))
        ret.append(text)
        ret.append(char * len(text))
        ret.append('')
        return ret

    def proces_version(self, version):
        return [':Version: {}'.format(version), '']

    def proces_description(self, desc):
        return [' '.join(x.strip() for x in desc.split('\n')).strip(), '']

    def _parse_initial_prefix(self, initial_prefix, len_list):
        """
        Parses the *initial_prefix* argument passed to :func:`proces_list`. If the
        type of *initial_prefix* is a list or a tuple, and its lenght is 1, it will
        return the first element. If its lenght is 2, it will check if *len_list*
        is greater than 1, if so it will return the second element of
        *initial_prefix*. If not it will return the first element.

        If the type of *initial_prefix* is not a list or a tuple, it is assumed to
        be a string type. In this case it will strip *initial_prefix* and force
        ending the prefix with ":" when *list_len* is 1, and ending with "s:" when
        *list_len* is greater than 1.

        :param initial_prefix: The *initial_prefix* argument passed to
                            :func:`proces_list`.
        :type initial_prefix: str or list[str] or tuple[str]
        :param int len_list: The lenght of the list passed to :func:`proces_list`.
        :return: The parsed prefix used for the first occurance in the list passed
                to :func:`proces_list`.
        :rtype: str
        """
        if type(initial_prefix) in [list, tuple]:
            if len(initial_prefix) == 1:
                return initial_prefix[0]
            elif not len(initial_prefix) == 2:
                raise ValueError("If 'initial_prefix' is passed as list or " +
                                "tuple,it must have a length of 1 or 2, not a " +
                                "length of {}.".format(len(initial_prefix)))
            if not len_list > 1:
                return initial_prefix[0]
            else:
                return initial_prefix[1]
        elif isinstance(initial_prefix, basestring):
            initial_prefix = initial_prefix.strip()
            if not len_list > 1:
                return initial_prefix.endswith('s:') and initial_prefix[:-2] + \
                    ':' or initial_prefix
            else:
                return initial_prefix.endswith('s:') and initial_prefix or \
                    initial_prefix[:-1] + 's:'

    def proces_list(self, list_, proces_func, initial_prefix='', prefix='', bullet='*'):
        ret = []
        if list_:
            bullet = bullet.strip()

            initial_prefix = self._parse_initial_prefix(initial_prefix, len(list_))
            prefix = prefix.strip()

            if initial_prefix and not prefix:
                prefix = ' '*len(initial_prefix)
            elif not initial_prefix and prefix:
                initial_prefix = prefix

            if not len(list_) > 1:
                for item in list_:
                    ret.append(' '.join([initial_prefix, proces_func(item)]))
            else:
                for item in list_:
                    if not ret:
                        ret.append(' '.join(
                            [initial_prefix, bullet, proces_func(item)]))
                    else:
                        ret.append(' '.join(
                            [prefix, bullet, proces_func(item)]))
            ret.append('')
        return ret

    def proces_person(self, person):
        if person.email is not None:
            return "`{name} <{email}>`_".format(name=person.name,
                                                email=person.email)
        else:
            return "{name}".format(name=person.name)

    def count_depends(self, pkg):
        return sum([len(getattr(pkg, x)) for x in PKG_DEPENDS.keys()])

    def has_depends(self, pkg):
        return self.count_depends(pkg) > 0

    def proces_dependency(self, dep):
        return ":ros:pkg:`{name}`".format(name=dep.name)

    def proces_url(self, url):
        if url.type:
            return "`{type} <{url}>`_".format(type=url.type.title(), url=url.url)
        else:
            return "{url}".format(url=url.url)

    def auto_package(self, pkg_name):
        rpkg = rospkg.RosPack()
        verbose = 'verbose' in self.options

        self.pkg_path = rpkg.get_path(pkg_name)
        pkg = catkin_pkg.package.parse_package(
            os.path.join(self.pkg_path,
                         catkin_pkg.package.PACKAGE_MANIFEST_FILENAME))

        ret = []
        ret += ['.. ros:package:: {}'.format(pkg.name), '']
        ret += self.make_heading('``' + pkg.name + '``', 'part')
        ret += self.make_toc(depth=1)
        ret += self.proces_description(pkg.description)
        ret += self.proces_list(pkg.authors, self.proces_person, initial_prefix=':Author:')
        ret += self.proces_list(pkg.maintainers, self.proces_person,
                        initial_prefix=':Maintainer:')
        ret += self.proces_list(pkg.urls, self.proces_url, initial_prefix=':Link:')
        ret += self.proces_version(pkg.version)
        ret += self.proces_list(pkg.licenses, str, initial_prefix=':License:')
        if self.has_depends(pkg):
            ret += self.make_heading('Dependencies', 'chapter')
            for dep in sorted(PKG_DEPENDS):
                pref = PKG_DEPENDS[dep]
                ret += self.proces_list(getattr(pkg, dep), self.proces_dependency,
                                initial_prefix=pref)
        msgs = self.get_msgs(pkg)
        if msgs:
            ret += self.make_heading('Messages', 'chapter')
            for msg in msgs:
                # TODO: This should not be necessary, demands change in the
                # sphinx_ros extension
                # msg = msg.replace('/', '.msg.')
                ret.append('.. ros:automessage:: {}'.format(msg))
                if verbose:
                    ret.append('   :verbose:')
                ret.append('')
            ret.append('')
        srvs = self.get_srvs(pkg)
        if srvs:
            ret += self.make_heading('Services', 'chapter')
            for srv in srvs:
                # TODO: This should not be necessary, demands change in the
                # sphinx_ros extension
                # srv = srv.replace('/', '.srv.')
                ret.append('.. ros:autoservice:: {}'.format(srv))
                if verbose:
                    ret.append('   :verbose:')
            ret.append('')
        acts = self.get_acts(pkg)
        if acts:
            ret += self.make_heading('Actions', 'chapter')
            for act in acts:
                ret.append('.. ros:autoaction:: {}'.format(act))
                if verbose:
                    ret.append('   :verbose:')
            ret.append('')
        ret += self.make_heading('Package definition files', 'chapter')
        ret += self.make_heading('CMakeLists.txt', 'section')
        ret += self.make_literalincluce('CMakeLists.txt', language='CMake')
        ret += self.make_heading('package.xml', 'section')
        ret += self.make_literalincluce('package.xml', language='xml')
        if 'verbose' in self.options:
            for line in ret:
                print(line)
        return ret
