"""OTRS :: ticket :: operations."""
from otrs.ticket.objects import Ticket as TicketObject
from otrs.client import OperationBase, authenticated, WrongOperatorException
from otrs.objects import extract_tagname, DynamicField


class Ticket(OperationBase):
    """Base class for OTRS Ticket:: operations."""


class TicketCreate(Ticket):
    """Class to handle OTRS Ticket::TicketCreate operation."""

    @authenticated
    def __call__(self, ticket, article, dynamic_fields=None,
                 attachments=None, **kwargs):
        """Create a new ticket.

        @param ticket a Ticket
        @param article an Article
        @param dynamic_fields a list of Dynamic Fields
        @param attachments a list of Attachments
        @returns the ticketID, TicketNumber
        """
        ticket_requirements = (
            ('StateID', 'State'), ('PriorityID', 'Priority'),
            ('QueueID', 'Queue'), )
        article_requirements = ('Subject', 'Body', 'Charset', 'MimeType')
        dynamic_field_requirements = ('Name', 'Value')
        attachment_field_requirements = ('Content', 'ContentType', 'Filename')
        ticket.check_fields(ticket_requirements)
        article.check_fields(article_requirements)
        if not (dynamic_fields is None):
            for df in dynamic_fields:
                df.check_fields(dynamic_field_requirements)
        if not (attachments is None):
            for att in attachments:
                att.check_fields(attachment_field_requirements)
        ret = self.req('TicketCreate', ticket=ticket, article=article,
                       dynamic_fields=dynamic_fields,
                       attachments=attachments, **kwargs)
        elements = self._unpack_resp_several(ret)
        infos = {extract_tagname(i): int(i.text) for i in elements}
        return infos['TicketID'], infos['TicketNumber']


class TicketGet(Ticket):
    """Class to handle OTRS Ticket::TicketGet operation."""

    @authenticated
    def __call__(self, ticket_id, get_articles=False,
                 get_dynamic_fields=False,
                 get_attachments=False, *args, **kwargs):
        """Get a ticket by id ; beware, TicketID != TicketNumber.

        @param ticket_id : the TicketID of the ticket
        @param get_articles : grab articles linked to the ticket
        @param get_dynamic_fields : include dynamic fields in result
        @param get_attachments : include attachments in result

        @return a `Ticket`, Ticket.articles() will give articles if relevant.
        Ticket.articles()[i].attachments() will return the attachments for
        an article, wheres Ticket.articles()[i].save_attachments(<folderpath>)
        will save the attachments of article[i] to the specified folder.
        """
        params = {'TicketID': str(ticket_id)}
        params.update(kwargs)
        if get_articles:
            params['AllArticles'] = True
        if get_dynamic_fields:
            params['DynamicFields'] = True
        if get_attachments:
            params['Attachments'] = True

        ret = self.req('TicketGet', **params)
        return TicketObject.from_xml(self._unpack_resp_one(ret))


class TicketSearch(Ticket):
    """Class to handle OTRS Ticket::TicketSearch operation."""

    @authenticated
    def __call__(self, dynamic_fields=None, **kwargs):
        """Search for a ticket by.

        @param dynamic_fields a list of Dynamic Fields, in addition to
        the combination of `Name` and `Value`, also an `Operator` for the
        comparison is expexted `Equals`, `Like`, `GreaterThan`,
        `GreaterThanEquals`, `SmallerThan` or `SmallerThanEquals`.
        The `Like` operator accepts a %-sign as wildcard.
        @returns a list of matching TicketID
        """
        df_search_list = []
        dynamic_field_requirements = ('Name', 'Value', 'Operator')
        if not (dynamic_fields is None):
            for df in dynamic_fields:
                df.check_fields(dynamic_field_requirements)
                if df.Operator == 'Equals':
                    df_search = DynamicField(Equals=df.Value)
                elif df.Operator == 'Like':
                    df_search = DynamicField(Like=df.Value)
                elif df.Operator == 'GreaterThan':
                    df_search = DynamicField(GreaterThan=df.Value)
                elif df.Operator == 'GreaterThanEquals':
                    df_search = DynamicField(GreaterThanEquals=df.Value)
                elif df.Operator == 'SmallerThan':
                    df_search = DynamicField(SmallerThan=df.Value)
                elif df.Operator == 'SmallerThan':
                    df_search = DynamicField(SmallerThan=df.Value)
                else:
                    raise WrongOperatorException()
                df_search.XML_NAME = 'DynamicField_{0}'.format(df.Name)
                df_search_list.append(df_search)
            kwargs['DynamicFields'] = df_search_list

        ret = self.req('TicketSearch', **kwargs)
        return [int(i.text) for i in self._unpack_resp_several(ret)]


class TicketUpdate(Ticket):
    """Class to handle OTRS Ticket::TicketUpdate operation."""

    @authenticated
    def __call__(self, ticket_id=None, ticket_number=None,
                 ticket=None, article=None, dynamic_fields=None,
                 attachments=None, **kwargs):
        """Update an existing ticket.

        @param ticket_id the ticket ID of the ticket to modify
        @param ticket_number the ticket Number of the ticket to modify
        @param ticket a ticket containing the fields to change on ticket
        @param article a new Article to append to the ticket
        @param dynamic_fields a list of Dynamic Fields to change on ticket
        @param attachments a list of Attachments for a newly appended article
        @returns the ticketID, TicketNumber


        Mandatory : - `ticket_id` xor `ticket_number`
                    - `ticket` or `article` or `dynamic_fields`

        """
        if not (ticket_id is None):
            kwargs['TicketID'] = ticket_id
        elif not (ticket_number is None):
            kwargs['TicketNumber'] = ticket_number
        else:
            raise ValueError('requires either ticket_id or ticket_number')

        if (ticket is None) and (article is None) and (dynamic_fields is None):
            raise ValueError(
                'requires at least one among ticket, article, dynamic_fields')
        elif (article is None) and not (attachments is None):
            raise ValueError(
                'Attachments can only be created for a newly appended article')
        else:
            if (ticket):
                kwargs['Ticket'] = ticket
            if (article):
                kwargs['Article'] = article
            if (dynamic_fields):
                kwargs['DynamicField'] = dynamic_fields
            if (attachments):
                kwargs['Attachment'] = attachments

        ret = self.req('TicketUpdate', **kwargs)
        elements = self._unpack_resp_several(ret)
        infos = {extract_tagname(i): int(i.text) for i in elements}
        return infos['TicketID'], infos['TicketNumber']
