"""OTRS :: ticket :: objects."""
from otrs.objects import Attachment
from otrs.objects import AttachmentContainer
from otrs.objects import DynamicField
from otrs.objects import DynamicFieldContainer
from otrs.objects import OTRSObject


class Article(OTRSObject, AttachmentContainer, DynamicFieldContainer):
    """An OTRS article."""

    XML_NAME = 'Article'
    CHILD_MAP = {'Attachment': Attachment, 'DynamicField': DynamicField}


class Ticket(OTRSObject, DynamicFieldContainer):
    """An OTRS ticket."""

    XML_NAME = 'Ticket'
    CHILD_MAP = {'Article': Article, 'DynamicField': DynamicField}

    def articles(self):
        """Return the articles for a ticket as a list.

        @returns a list of Article objects.
        """
        try:
            return self.childs['Article']
        except KeyError:
            return []
