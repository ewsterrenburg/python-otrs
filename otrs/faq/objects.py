"""OTRS :: faq :: objects."""
from otrs.objects import Attachment
from otrs.objects import AttachmentContainer
from otrs.objects import OTRSObject


class Category(OTRSObject):
    """An OTRS FAQ Category."""

    XML_NAME = 'Category'


class Language(OTRSObject):
    """An OTRS FAQ Language."""

    XML_NAME = 'Language'


class FAQItem(OTRSObject, AttachmentContainer):
    """An OTRS FAQ Item."""

    XML_NAME = 'FAQItem'
    CHILD_MAP = {'Attachment': Attachment}
