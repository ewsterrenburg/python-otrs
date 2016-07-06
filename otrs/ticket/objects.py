from ..objects import OTRSObject

class Attachment(OTRSObject):
    XML_NAME = 'Attachment'

class DynamicField(OTRSObject):
    XML_NAME = 'DynamicField'

class Article(OTRSObject):
    XML_NAME = 'Article'
    CHILD_MAP = {'Attachment': Attachment, 'DynamicField': DynamicField}

    def attachments(self):
        try:
            return self.childs['Attachment']
        except KeyError:
            return []

    def dynamicfields(self):
        try:
            return self.childs['DynamicField']
        except KeyError:
            return []

    def save_attachments(self, folder):
        """ Saves the attachments of an article to the specified folder

        @param folder  : a str, folder to save the attachments
        """
        for a in self.attachments():
            fname = a.attrs['Filename']
            fpath = os.path.join(folder, fname)
            content = a.attrs['Content']
            fcontent = base64.b64decode(content)
            ffile = open(fpath, 'wb')
            ffile.write(fcontent)
            ffile.close()


class Ticket(OTRSObject):
    XML_NAME = 'Ticket'
    CHILD_MAP = {'Article': Article, 'DynamicField': DynamicField}

    def articles(self):
        try:
            return self.childs['Article']
        except KeyError:
            return []

    def dynamicfields(self):
        try:
            return self.childs['DynamicField']
        except KeyError:
            return []
