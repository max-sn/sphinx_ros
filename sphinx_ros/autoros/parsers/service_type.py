import os
import re

from .message_type import MessageTypeParser
from ..objects import DocRosServiceType


class ServiceTypeParser(MessageTypeParser):

    subtype = 'srv'

    def init_msg_list(self, src_name):
        # Create a DocSrv instance
        self.item = DocRosServiceType(src_name, self.pkg)
        # Return its messages as a list
        return [self.item.request, self.item.response]
