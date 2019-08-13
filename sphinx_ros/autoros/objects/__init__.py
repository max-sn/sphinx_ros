class DocRosObject(object):
    """
    Parent class for all objects that should be documented in a ROS workspace.

    :ivar str name: Name for the object.
    """

    def __init__(self, name='', description=[], parent=None):
        #: Name for the object.
        self.name = name
        #: Description for the object. Every list item represents a paragraph.
        self.description = description
        #: If the object has a parent, this can be set when adding it to the
        #: parents collection.
        self.parent = parent


class DocRosWorkspace(DocRosObject):
    """
    Class to describe a workspace.
    """

    def __init__(self, name='', description=[], parent=None):
        super(DocRosObject, self).__init__(self, name, description, parent)
        #: List of packages contained in the workspace.
        self.packages = []

    def add_package(self, pkg):
        pkg.parent = self
        self.packages.append(pkg)

    def get_doc_str_list(self):
        """
        This method will iterate over all children of the workspace to generate
        a documentation string. This string can then be used to parse with a
        Sphinx parser.

        :return: The complete documentation of the workspace.
        :rtype: list[str]
        """
        return []


class DocRosParam(DocRosObject):
    """
    Class to describe parameters that make up message types.
    """

    def __init__(self, name='', description=[], parent=None, type_=''):
        super(DocRosParam, self).__init__(name, description, parent)
        #: Type of the parameter. This could be a ROS messsage type itself.
        self.type = type_


class DocRosMessageType(DocRosObject):
    """
    Describes a ROS message type definition.
    """

    def __init__(self, name='', description=[], parent=None):
        super(DocRosMessageType, self).__init__(name, description, parent)
        #: List of parameters included in the message type. There type can be a
        #: ROS message type again, but in the workspace documentation tree they
        #: will be treated as parameters only.
        self.params = []

    def add_param(self, param):
        param.parent = self
        self.params.append(param)


class DocRosServiceType(DocRosObject):
    """
    Describes a ROS service type definition.
    """

    def __init__(self, name='', description=[], parent=None):
        super(DocRosServiceType, self).__init__(name, description, parent)
        #: The message send as a request to a provided service.
        self.request = DocRosMessageType()
        #: The response from the provided service.
        self.response = DocRosMessageType()


class DocRosActionType(DocRosObject):
    """
    Describes a ROS actionlib action type definition.
    """

    def __init__(self, name='', description=[], parent=None):
        super(DocRosActionType, self).__init__(name, description, parent)
        #: The message sent to set the goal of an action.
        self.goal = DocRosMessageType()
        #: The message sent when the action is completed.
        self.result = DocRosMessageType()
        #: The message sent during the action to keep track of the process.
        self.feedback = DocRosMessageType()
