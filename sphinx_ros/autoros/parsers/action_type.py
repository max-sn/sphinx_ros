import os
import re

from .message_type import MessageTypeParser
from ..objects import DocRosActionType


class ActionTypeParser(MessageTypeParser):

    subtype = 'action'

    def init_msg_list(self, src_name):
        # Create a DocAction instance
        self.item = DocRosActionType(src_name, self.pkg)
        # Return its messages as a list
        return [self.item.goal, self.item.result, self.item.feedback]
