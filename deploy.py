import sys
import os
from ftplib import FTP, error_perm
from getpass import getpass

from pathlib import PureWindowsPath as wpath

EXCLUDE_DIRS = ['.git', '.vscode']
EXCLUDE_FILES = ['deploy.py', '.gitignore']

def make_data_list():
    top = os.getcwd()
    folders = []
    files = []
    for dirpath, dirnames, filenames in os.walk(top):
        if any([True for ex in EXCLUDE_DIRS if ex in dirpath]):
            continue

        root = make_relative(dirpath)
        dirs = [dir for dir in dirnames if dir not in EXCLUDE_DIRS]
        f_filenames = [file for file in filenames if file not in EXCLUDE_FILES]

        [folders.append(os.path.join(root, dir)) for dir in dirs]
        [files.append(os.path.join(root, file)) for file in f_filenames]
            
    return (folders, files)

def make_relative(path):
    res = os.path.relpath(path, os.getcwd())
    
    if res == '.':
        return ''
    else:
        return res

class FTPConnection:
    def __init__(self, host, user, pwd):
        self.conn = FTP(host)

        try:
            self.conn.login(user, pwd)
        except error_perm:
            print("Login credentials invalid.")

        print("FTP connection successful")

    def clean(self):
        print("I will now delete all existing files and folders. Continue? [y/N]")
        res = input().lower()

        if res != 'y':
            print('Exiting...')
            sys.exit()

        print("Cleaning data...")
        contents = self._get_structure()
        self._delete_structure(contents)

    def _get_structure(self, root=''):
        data = self.conn.nlst(root)

        if len(data) == 1 and data[0] == root:
            return False

        contents = []
        for entry in data:
            res = self._get_structure(entry)
            if res:
                contents.append(res)
            contents.append(entry)
        
        return contents

    def _delete_structure(self, content):
        content = [item for item in content if item not in EXCLUDE_FILES]

        for item in content:
            if isinstance(item, str):
                print('deleting file\t', item, '...')
                if '.' in item or 'LICENSE' in item:
                    self.conn.delete(item)
                else:
                    self.conn.rmd(item)
            else:
                self._delete_structure(item)

    def upload_data(self, directories, files):
        self._make_directories(directories)
        self._upload_files(files)

    def _make_directories(self, directories):
        for dir in directories:
            print("create", dir, "...")
            self.conn.voidcmd('mkd {0}'.format(wpath(dir).as_posix()))

    def _upload_files(self, files):
        for file in files:
            print ('uploading', file, '...')
            with open(file, "rb") as f:
                self.conn.storbinary('stor {0}'.format(wpath(file).as_posix()), f)


if __name__ == '__main__':
    host = input("Enter target host:")
    user = input("Enter username:")
    pwd = getpass("Enter password:")
    conn = FTPConnection(host, user, pwd)
    (folders, files) = make_data_list()
    conn.clean()
    conn.upload_data(folders, files)
