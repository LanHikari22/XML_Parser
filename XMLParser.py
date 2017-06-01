from AbstractXMLParserHandler import AbstractXMLParserHandler
import io

class _XMLTag:
    name = str
    attributes = dict() # no init and {} or dict() makes this static?!
    characters = str
    # Tag Tree Hierachy
    parent = None
    children = list() # no init and [] or list() makes this static?!
    # Tag construction: Only valid if both start and end tags are valid
    hasStartElement = False
    hasEndElement = False

    def __init__(self):
        self.name = None
        self.attributes = {}
        self.characters = None
        self.parent = None
        self.children = []
        self.hasStartElement = False
        self.hasEndElement = False


##
# Scans through each line, character by character, performing some heavy logic to parse XML
# Params:
#   - file: file object to be parsed
# Returns:
#   Root tag, which has all child tags contained within the XML file
##
def _handleParsing(file):
    tagCsr = _XMLTag()
    tagCsr.parent = None  # root tag is the first
    key = ''
    value = ''
    endName = ''
    firstLine = True
    status = {"tagElement": "", "field": "", "startBrac": False, "openQuote": False, "encounteredEquals": False}

    for line in file:
        # Skip first line, if it's this
        if line == '<?xml version="1.0"?>\n' and firstLine:
            firstLine = False
            continue

        # Parse through every character in each line
        for i in range(len(line)):
            # Debugging vars
            remainingLine = line[i:]
            currChar = line[i]
            nextChar = line[i + 1] if (i < len(line) - 2) else None
            # White space is permitted.
            if not tagCsr.hasStartElement and line[i].isspace():
                continue

            if line[i] == "<" and not status["openQuote"]:
                if i < len(line) - 2:  # Ensures next character is not last. (Last should be '\n')
                    if (line[i + 1] == "/"):  # Case: "</"
                        # Current tag has <> but not </> and no repeated angle brackets occur
                        if (tagCsr.hasStartElement and not tagCsr.hasEndElement and not status["startBrac"]):
                            status["startBrac"] = True
                            status["tagElement"] = "endElement"
                            # This better be </name> where name is the current tag name.
                        else:
                            raise Exception("Corrupted XML File: Invalid end element of tag")
                    else:  # Case: "<"
                        # Starting a new tag before ending current one
                        if tagCsr.hasStartElement and not tagCsr.hasEndElement:
                            temp = _XMLTag()
                            temp.parent = tagCsr
                            tagCsr.children.append(temp)
                            tagCsr = temp  # Advancing cursor, now in the child tag
                        # Current tag doesn't have <> or </> and no repeated angle brackets occur
                        if not tagCsr.hasStartElement and not tagCsr.hasEndElement and not status["startBrac"]:
                            status["startBrac"] = True
                            status["tagElement"] = "startElement"
                        else:
                            raise Exception("Corrupted XML File: Invalid start element of tag")

            elif line[i] == ">" and not status["openQuote"]:
                status["startBrac"] = False
                if status["tagElement"] == "startElement":
                    status["tagElement"] = ""
                    tagCsr.hasStartElement = True
                elif status["tagElement"] == "endElement" and tagCsr.hasStartElement:
                    status["tagElement"] = ""
                    tagCsr.hasEndElement = True
                    # Ensure endName and the tag cursor's name match
                    if tagCsr.name == endName:
                        endName = ''
                    else:
                        raise Exception("Corrupted XML File: start and end elements don't match")

                    # This tag is now over, returning to parent tag, or ending.
                    if tagCsr.parent == None:
                        break
                    else:
                        tagCsr = tagCsr.parent

                else:
                    raise Exception("Corrupted XML File: invalid end element")

            # Only one syntactical '=' should be encountered in startElement. Next char must not be last. No quotes open.
            elif line[i] == "=" and not status["openQuote"] and not tagCsr.hasStartElement and i < len(line) - 2:
                if not status["encounteredEquals"]:
                    status["encounteredEquals"] = True
                else:
                    raise Exception("Corrupted XML File: encountered more than one '='")
                # whitespace after '=' not allowed
                if line[i + 1] != '"':
                    raise Exception(
                        'Corrupted XML File: whitespace between key and value in key="value" is not allowed')

            # When the character is not a syntactical '=' and is in startElement. Next char must not be last.
            elif (line[i].isprintable()) and not tagCsr.hasStartElement and i < len(line) - 2:
                if status["field"] == "":
                    if tagCsr.name == None:
                        status["field"] = "name"
                        tagCsr.name = line[i]
                    else:
                        status["field"] = "attr"
                        key += line[i]
                elif status["field"] == "name":
                    tagCsr.name += line[i]
                    # Done parsing name!
                    if line[i + 1].isspace() or line[i + 1] == ">":
                        status["field"] = ""
                elif status["field"] == "attr":
                    if status["encounteredEquals"]:  # after '='. ie, parsing a value
                        # Start quote! Must come after '='.
                        if line[i] == '"' and line[i - 1] == '=' and not status["openQuote"]:
                            status["openQuote"] = True
                        # End Quote! Key="value" gathered. Add to tag and update status and reset key/value temp vars
                        elif line[i] == '"' and status["openQuote"]:
                            status["openQuote"] = False
                            tagCsr.attributes[key] = value
                            # reset key/value temp vars
                            key = ''
                            value = ''
                            # reset field status
                            status["field"] = ''
                            # We've no longer encountered equals for the potential next attribute
                            status["encounteredEquals"] = False
                        elif line[i] != '"' and status["openQuote"]:
                            value += line[i]
                        else:
                            raise Exception("Corrupted XML File: values not found within quotes in attributes")
                    else:  # before '='. ie, parsing a key
                        key += line[i]
                        if line[i + 1].isspace():
                            raise Exception(
                                'Corrupted XML File: whitespace between key and value in key="value" is not '
                                'allowed')

            # Characters
            elif (line[i].isprintable()) and tagCsr.hasStartElement \
                    and not tagCsr.hasEndElement and status["tagElement"] != "endElement":
                if line[i] == '"':
                    status["openQuote"] = not status["openQuote"]
                if tagCsr.characters is not None:
                    tagCsr.characters += line[i]
                else:
                    tagCsr.characters = line[i]

            # End Element name, ensure <tag> ends with </tag>
            elif (line[i].isprintable()) and tagCsr.hasStartElement \
                    and not tagCsr.hasEndElement and status["tagElement"] == "endElement":
                # Do this for all characters except '/' in "</"
                if line[i - 1:i + 1] != "</":
                    endName += line[i]
    return tagCsr


##
# Recursive function. Traverses the Tags tree, calling startElement(), endElement() for each.
# characters() is only called when the tag contains characters in between <tag> </tag>
# Returns:
#   Nothing
##
def echoTags(tag = _XMLTag,handler = AbstractXMLParserHandler):
    # Call startElement() and pass attributes
    handler.startElement(tag.name, tag.attributes)
    # Call characters() if possible
    if tag.characters.strip(' ') != None and not tag.characters.isspace():
        handler.characters(tag.characters.strip(' '))
    # Traverse down, if there are children
    for child in tag.children:
        echoTags(child, handler)
    # Call endElement()
        handler.endElement(tag.name)

##
# Parser class.
# Parses through XML files and called abstractParserHandler functions
# startElement(), endElement(), and characters() reporting the data found.
##
class XMLParser:

    # File to be parsed
    _filename = None

    ##
    # Sets the filename to be parsed
    # Params:
    #   filename - file path to the file to be parsed
    # Returns:
    #   Nothing
    ##
    def __init__(self, filename = str):
        self._filename = filename

    ##
    # Parses _file and calls startElement(), endElement() and characters()
    # from a parser handler class.
    # Returns:
    #   Nothing
    ##
    def parse(self):
        file = open(self._filename, "r")
        rootTag = _handleParsing(file)
        echoTags(rootTag,AbstractXMLParserHandler()) # Calls the appropriate startElement(), endElement() and characters() functions
        print(rootTag)
