import rospkg
import os
import glob


class ParserTemplate():

    subtype = None
    target_ext = '.txt'

    def __init__(self, pkg, item=None, src_path=None, target_path=None):
        self.items = []
        self.set_pkg(pkg, src_path, target_path)
        self.find_src_files(item)
        if self.src_files:
            self.create_target_dir()

    def set_pkg(self, pkg, src_path=None, target_path=None):
        self.pkg = pkg
        try:
            self.pkg_path = rospkg.RosPack().get_path(self.pkg)
        except rospkg.ResourceNotFound:
            print('Package not found by rospkg. Please make sure that the ' +
                  'workspace containing the package is sourced.')
            raise e
        if src_path is None:
            self.src_path = os.path.join(self.pkg_path, self.subtype)
        if target_path is None:
            self.target_path = os.path.join(self.pkg_path, 'doc', self.subtype)
        self.src_files = None

    def find_src_files(self, item=None):
        if os.path.exists(self.src_path):
            if item is None:
                self.src_files = glob.glob(self.src_path + '/*.' +
                                           self.subtype)
            else:
                self.src_files = [os.path.join(self.src_path, item + '.' +
                                               self.subtype)]

    def create_target_dir(self):
        if not os.path.exists(self.target_path):
            os.makedirs(self.target_path)

    def export(self):
        for item in self.items:
            target_file = os.path.join(self.target_path,
                                       item.name + self.target_ext)
            with open(target_file, 'w') as f:
                for ln in item.str:
                    f.write(ln + '\n')
