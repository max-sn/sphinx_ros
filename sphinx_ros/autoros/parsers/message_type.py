import os
import re

from . import ParserTemplate
from ..objects import DocRosParam, DocRosMessageType


class MessageTypeParser(ParserTemplate):

    subtype = 'msg'

    def process_line(self, line):
        # Determine current state (might be not robust enough)
        if line.startswith('#::'):
            state = 'src_desc'
            # Cut '#::' from line.
            line = line[3:]
        elif line.startswith('#:'):
            state = 'param_desc'
            # Cut '#:' from line.
            line = line[2:]
        elif line.startswith('#'):
            state = 'comment'
        elif line.strip() == '':
            state = 'empty'
        elif line.strip() == '---':
            state = 'next_msg'
        else:
            state = 'param'

        if state == 'src_desc':
            if not self.description_list:
                # If description_list is still empty, only get the
                # current line as item.
                self.description_list.append(line.strip())
            else:
                # If not, check furthur.
                if self.previous_state == 'src_desc':
                    # If already coming from 'src_desc' state, then
                    # check if line is only whitespace with a line
                    # end.
                    if line.strip(' ') == '\n':
                        # If so, add an empty line to which the
                        # entry can be appended. (No empty lines
                        # should remain in this list)
                        self.description_list.append('')
                    else:
                        # If not, check if the last entry is not an
                        # empty string. If it is not, add a space
                        # as seperator and append the current line.
                        if not self.description_list[-1] == '':
                            self.description_list[-1] += ' '
                        self.description_list[-1] += line.strip()
                else:
                    # If coming from a different state, add the
                    # current line as a new entry. There should be
                    # a line break in the resulting document.
                    self.description_list.append(line.strip())

        elif state == 'param':
            # First strip trailing comments and whitespace.
            line = re.sub(r'#.*$', '', line).strip()
            # Then split on the space to get the type and name of
            # parameter.
            (typ, name) = line.split(' ', 1)
            # Create a new DocRosParam instance. The value of
            # 'param_desc' is already set, or it might be empty.
            param = DocRosParam(name, self.param_desc, type_=typ)
            # Add this DocRosParam instance to the list of parameters
            # of this item.
            self.msg_list[self.msg_idx].add_param(param)

        elif state == 'param_desc':
            # Parameter descriptions should be one or more lines
            # without omitting the '#:' prefix. Therefore, if the
            # previous state is not 'param_desc', the description
            # will be reset.
            if not self.previous_state == 'param_desc':
                self.param_desc = ''
            elif not self.param_desc == '':
                self.param_desc += ' '

            # Strip all whitespace from the line. Parameter
            # descriptions should not have line breaks.
            self.param_desc += line.strip()

        elif state == 'comment' or state == 'empty':
            # If comment or empty line, just skip the line.
            pass

        elif state == 'next_msg':
            # If the type description ends with an empty line, this
            # reflects in the 'description_list' so here we remove
            # it.
            if self.description_list:
                if self.description_list[-1].strip() == '':
                    del self.description_list[-1]

            # Send results to DocRosMessageType instance and generate
            # documentation string.
            self.msg_list[self.msg_idx].description = self.description_list

            # Re-initialize DocRosMessageType describing variables
            self.description_list = []
            self.param_desc = ''
            self.state = ''

            self.msg_idx += 1

        # Track state to one step back
        self.previous_state = state

    def init_msg_list(self, src_name):
        # Create a DocRosMessageType instance
        self.item = DocRosMessageType()
        self.item.name = src_name
        # Return it as a list
        return [self.item]

    def parse(self, pkg=None):

        for src in self.src_files:
            with open(src, 'r') as f:
                # Split src into path, basename, and extension
                (path, fn) = os.path.split(src)
                (src_name, _) = os.path.splitext(fn)

                self.msg_list = self.init_msg_list(src_name)
                self.msg_idx = 0

                # Initialize DocRosMessageType describing variables
                self.description_list = []
                self.param_desc = ''
                self.previous_state = ''

                # Read file line by line
                for line in f.readlines():
                    self.process_line(line)

                # If the type description ends with an empty line, this
                # reflects in the 'description_list' so here we remove it.
                if self.description_list:
                    if self.description_list[-1].strip() == '':
                        del self.description_list[-1]

                # Send results to DocRosMessageType instance
                self.msg_list[self.msg_idx].description = self.description_list
                # Finally add the item to parser's list of items.
                self.items.append(self.item)

        return self.item
