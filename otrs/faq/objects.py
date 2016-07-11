from ..objects import OTRSObject, Attachment, AttachmentContainer

class Category(OTRSObject):
    XML_NAME = 'Category'

class Language(OTRSObject):
    XML_NAME = 'Language'

class FAQItem(OTRSObject, AttachmentContainer):
    XML_NAME = 'FAQItem'
    CHILD_MAP = {'Attachment': Attachment}
