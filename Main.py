import os
import sys
from XMLParser import XMLParser
from enum import Enum

ESC_RESET = "\033[0m"
ESC_HEADER = '\033[95m'
ESC_BLUE = '\033[94m'
ESC_GREEN = '\033[92m'
ESC_WARNING = '\033[93m'
ESC_FAIL = '\033[91m'
ESC_BOLD = '\033[1m'
ESC_UNDERLINE = '\033[4m'


# Returns "\033[" + cmd + "m"
def genEsc(cmd=int):
    return "\033[%um" % (cmd & 0xFF)  # unsigned cast to 8-bit


# Shows valid escape sequences
def printEsc():
    for i in range(107):
        print("%u] %sHello World!!%s" % (i, genEsc(i), ESC_RESET))




    # def __init__(self, parent):
    #     self.parent = parent
    #
    # def __init__(self, name, parent):
    #     self.__init__(parent)
    #     self.name = name
    #
    # def __init__(self, name, attributes, characters, parent, children, hasStartElement, hasEndElement):
    #     self.__init__(name, parent)
    #     self.attributes = attributes
    #     self.characters = characters
    #     self.children = children
    #     self.hasStartElement = hasStartElement
    #     self.hasEndElement = hasEndElement


if __name__ == "__main__":
    line = '   <book id="bk101" version="1.0" name="The Legends of Zelda... and <Link!>">\n</book>'
    parser = XMLParser("books.xml")
    parser.parse()



## main0
# if __name__ == "__main0__":
#         dict = {"apple":0, "orange":1}
#         # print("My favorite number is %i" % dict["apple"])
#         file = open("books.xml", "r")
#         for line in file:
#             print(line, end='')
#         print("atty? " + ("yes" if file.isatty() else "no"))
#         print("seekable? " + ("no", "yes")[file.seekable()])
##
