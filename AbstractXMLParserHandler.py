##
# Can be disabled within function, or overridden. prints to stdout when enabled
# Params:
#   - newLine: determines whether to print a new line or not
# Returns:
#   Nothing
##
def log(s, newLine = bool):
    logEnabled = True
    if logEnabled and newLine:
        print(s)
    elif logEnabled and not newLine:
        print(s, end='')

##
# ParserHandler class.
# This handles what happens when the startElement(), endElement() and characters() functions are called.
# extend this and override its functions for a specialized use of the XML parser.
##
class AbstractXMLParserHandler:


    ##
    #Gets called when the parser finds the start of an element.
    # Params:
    #   name - Element tag name.
    #   attributes - Any potential attributes defined within the element tag
    # Returns:
    #   Nothing
    ##
    def startElement(self, name = str, attributes = dict):

        log("[+] Found start of element: <%s>" % name)
        if attributes != {}:
            log("Attributes: {", False)
        temp = ''
        for attr in attributes:
            temp += ('%s="%s", ' % (attr, attributes[attr])) # no new line
        if attributes != {}:
            temp = temp[:-2] + "}\n"
        log(temp, False)
        return


    ##
    # Gets called when the parser finds the end of an element
    # Params:
    #   name - Element tag name
    # Returns:
    #   Nothing
    ##
    def endElement(self, name = str):

        log("[-] Found end of element: </%s>" % name)
        return

    ##
    # Gets called when the parser finds characters between elements
    # Params:
    #   data - characters found between start and end element
    # Returns:
    #   Nothing
    ##
    def characters(self, data = str):
        log("Characters found:\n%s" % data)
        return
