"""
``sphinx_ros.indices`` module
=============================

This modules defines the indices added to Sphinx.
"""
from six import iteritems
from sphinx.domains import Index


class RosMessageIndex(Index):
    """
    Index listing the documented message types.
    """

    name = 'msgindex'
    localname = 'Message Type Index'
    shortname = 'msgs'

    def generate(self, docnames=None):
        content = {}
        # Get messages from domain data
        messages = self.domain.data['messages']
        base_messages = {}

        # Split package name and make new dict.
        # name -> document name, anchor, priority, deprecated
        for msgname, (docname, anchor, _, deprecated) in iteritems(messages):
            pkgname, _, base_msgname = msgname.split('.')
            base_messages[base_msgname] = (pkgname, docname, anchor,
                                           deprecated)

        # Sort the messages in alphabetical order
        base_messages = sorted(iteritems(base_messages),
                               key=lambda x: x[0].lower())

        # base_name -> pkg name, document name, anchor, deprecated
        for base_msgname, (pkg, docname, anchor, deprecated) in base_messages:
            if docnames and docname not in docnames:
                continue

            if base_msgname[0].lower() in content:
                entries = content[base_msgname[0].lower()]
            else:
                entries = []

            qualifier = deprecated and 'Deprecated' or ''
            entries.append([base_msgname + ' (in {})'.format(pkg), 0,
                            docname, anchor, '', qualifier, ''])
            content[base_msgname[0].lower()] = entries

        content = sorted(content.items())

        return content, True


class RosPackageIndex(Index):
    """
    Index listing the documented packages.
    """

    name = 'pkgindex'
    localname = 'Package Index'
    shortname = 'pkgs'

    def generate(self, docnames=None):
        content = {}

        # Sort the packages in alphabetical order
        packages = sorted(iteritems(self.domain.data['packages']),
                          key=lambda x: x[0].lower())

        # name -> document name, anchor, priority, deprecated
        for pkgname, (docname, anchor, _, deprecated) in packages:
            if docnames and docname not in docnames:
                continue

            if pkgname[0].lower() in content:
                entries = content[pkgname[0].lower()]
            else:
                entries = []

            qualifier = deprecated and 'Deprecated' or ''
            entries.append([pkgname, 0, docname, anchor, '', qualifier, ''])
            content[pkgname[0].lower()] = entries

        content = sorted(content.items())

        return content, True
