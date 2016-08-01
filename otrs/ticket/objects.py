"""OTRS :: ticket :: objects."""
from otrs.objects import OTRSObject, Attachment, DynamicField
from otrs.objects import AttachmentContainer, DynamicFieldContainer


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
