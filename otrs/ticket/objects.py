from ..objects import OTRSObject, Attachment, DynamicField, AttachmentContainer, DynamicFieldContainer

class Article(OTRSObject, AttachmentContainer, DynamicFieldContainer):
    XML_NAME = 'Article'
    CHILD_MAP = {'Attachment': Attachment, 'DynamicField': DynamicField}

class Ticket(OTRSObject, DynamicFieldContainer):
    XML_NAME = 'Ticket'
    CHILD_MAP = {'Article': Article, 'DynamicField': DynamicField}

    def articles(self):
        try:
            return self.childs['Article']
        except KeyError:
            return []
