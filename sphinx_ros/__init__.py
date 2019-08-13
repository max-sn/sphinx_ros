"""
``sphinx_ros`` module
=====================

Sphinx extension adding several directives to document ROS packages.
"""

from pkg_resources import get_distribution, DistributionNotFound

try:
    from sphinx.domains import StandardDomain
except ImportError:
    from sphinx.domains.std import StandardDomain
from .domain import RosDomain

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # Package is not installed
    __version__ = 'unknown'


def setup(app):
    """
    Adds the ROS domain to the Sphinx application and the labels to the ROS
    indices to the standard domain. It also adds the configuration values
    :confval:`ros_add_package_names` and :confval:`ros_msg_reference_version`.

    :param app: The Sphinx application
    :type app: sphinx.application.Sphinx
    """
    app.add_domain(RosDomain)

    app.add_config_value('ros_add_package_names', True, 'html')
    app.add_config_value('ros_msg_reference_version', 'melodic', 'html')

    StandardDomain.initial_data['labels'].\
        update(RosDomain.initial_data['labels'])
    StandardDomain.initial_data['anonlabels'].\
        update(RosDomain.initial_data['anonlabels'])

    return {
        'version': __version__,
        'parallel_read_safe': False,
        'parallel_write_safe': True
    }
