"""
``sphinx_autoros`` module
=========================

Sphinx extension automating the documentation of ROS packages.
"""
from .directives.autopackage import RosAutoPackageDirective
from .directives.automessage import RosAutoMessageDirective
from .directives.autoservice import RosAutoServiceDirective
from .directives.autoaction import RosAutoActionDirective


# def setup(app):

#     app.require_sphinx('1.8')
#     app.setup_extension('sphinx_ros')
#     app.add_directive_to_domain('ros', 'autopackage', RosAutoPackageDirective)
#     app.add_directive_to_domain('ros', 'automessage', RosAutoMessageDirective)
#     app.add_directive_to_domain('ros', 'autoservice', RosAutoServiceDirective)
#     app.add_directive_to_domain('ros', 'autoaction', RosAutoActionDirective)

#     return {
#         'version': '0.1',
#         'parallel_read_safe': True,
#         'parallel_write_safe': True}
