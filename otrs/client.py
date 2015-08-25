import urllib2
from posixpath import join as urljoin
import xml.etree.ElementTree as etree
from .objects import Ticket, OTRSObject, DynamicField, extract_tagname

class OTRSError(Exception):
    def __init__(self, fd):
        self.code = fd.getcode()
        self.msg = fd.read()

    def __str__(self):
        return '{} : {}'.format(self.code, self.msg)

class SOAPError(OTRSError):
    def __init__(self, tag):
        d = {extract_tagname(i): i.text for i in tag.getchildren()}
        self.errcode = d['ErrorCode']
        self.errmsg = d['ErrorMessage']

    def __str__(self):
        return '{} ({})'.format(self.errmsg, self.errcode)


class NoCredentialsException(OTRSError):
    def __init__(self):
        pass
    def __str__(self):
        return 'Register credentials first with register_credentials() method'

class WrongOperatorException(OTRSError):
    def __init__(self):
        pass
    def __str__(self):
        return '''Please use one of the following operators for the
               query on a dynamic field: 'Equals', 'Like', 'GreaterThan',
               'GreaterThanEquals', 'SmallerThan', 'SmallerThanEquals'
               '''

def authenticated(func):
    """ Decorator to add authentication parameters to a request
    """
    def add_auth(self, *args, **kwargs):
        if self.session_id:
            kwargs['SessionID'] = self.session_id
        elif self.login and self.password:
            kwargs['UserLogin'] = self.login
            kwargs['Password'] = self.password
        else:
            raise NoCredentialsException()

        return func(self,*args, **kwargs)
    return add_auth

SOAP_ENVELOPPE = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns="http://www.otrs.org/TicketConnector/">
  <soapenv:Header/>
  <soapenv:Body>{}</soapenv:Body>
</soapenv:Envelope>
"""

class GenericTicketConnector(object):
    """ Client for the GenericTicketConnector SOAP API

    see http://otrs.github.io/doc/manual/admin/3.3/en/html/genericinterface.html
    """

    def __init__(self, server, webservice_name='GenericTicketConnector'):
        """ @param server : the http(s) URL of the root installation of OTRS
                            (e.g: https://tickets.example.net)

            @param webservice_name : the name of the installed webservice
                   (choosen by the otrs admin).
        """

        self.endpoint = urljoin(
            server,
            'otrs/nph-genericinterface.pl/Webservice/',
            webservice_name)
        self.login = None
        self.password = None
        self.session_id = None

    def register_credentials(self, login, password):
        """ Save the identifiers in memory, they will be used with each
            subsequent request requiring authentication
        """
        self.login = login
        self.password = password

    def req(self, reqname, *args, **kwargs):
        """ Wrapper arround a SOAP request
        @param reqname: the SOAP name of the request
        @param kwargs : to define the tags included in the request.
        @return       : the full etree.Element of the response

        keyword arguments can be either
         - simple types (they'l be converted to <name>value</name>)
         - `OTRSObject`, they will be serialized with their `.to_xml()`
         - list of  `OTRSObject`s: each  `OTRSObject`s in the list
           will be serialized with their `.to_xml()` (used for
           dynamic fields and attachments).

        """
        xml_req_root = etree.Element(reqname)

        for k,v in kwargs.items():
            if isinstance(v, OTRSObject):
                e = v.to_xml()
                xml_req_root.append(e)
            elif type(v) == list:
                for vv in v:
                    xml_req_root.append(vv.to_xml())
            else:
                e = etree.Element(k)
                e.text = str(v)
                xml_req_root.append(e)

        request = urllib2.Request(
            self.endpoint, self._pack_req(xml_req_root),
            {'Content-Type': 'text/xml;charset=utf-8'}
        )
        print self._pack_req(xml_req_root)
        fd = urllib2.urlopen(request)
        if fd.getcode() != 200:
            raise OTRSError(fd)
        else:
            try:
                s = fd.read()
                e = etree.fromstring(s)

                unpacked = self._unpack_resp_several(e)
                if (len(unpacked) > 0) and (unpacked[0].tag.endswith('Error')):
                    raise SOAPError(unpacked[0])
                return e
            except etree.ParseError:
                print('error parsing:')
                print('-'*80)
                print(s)
                print('-'*80)
                raise

    @staticmethod
    def _unpack_resp_several(element):
        """
        @param element : a etree.Element
        @return        : a list of etree.Element
        """
        return element.getchildren()[0].getchildren()[0].getchildren()

    @staticmethod
    def _unpack_resp_one(element):
        """
        @param element : a etree.Element
        @return        : a etree.Element (first child of the response)
        """
        return element.getchildren()[0].getchildren()[0].getchildren()[0]

    @staticmethod
    def _pack_req(element):
        """
        @param element : a etree.Element
        @returns       : a string, wrapping element within the request tags

        """
        return SOAP_ENVELOPPE.format(etree.tostring(element))

    def session_create(self, password, user_login=None,
                                       customer_user_login=None):
        """ Logs the user or customeruser in

        @returns the session_id
        """
        if user_login:
            ret = self.req('SessionCreate',
                           UserLogin = user_login,
                           Password  = password)
        else:
            ret = self.req('SessionCreate',
                           CustomerUserLogin = customer_user_login,
                           Password          = password)
        signal = self._unpack_resp_one(ret)
        session_id = signal.text
        return session_id

    def user_session_register(self, user, password):
        """ Logs the user in and stores the session_id for subsequent requests
        """
        self.session_id = self.session_create(
            password=password,
            user_login=user)

    def customer_user_session_register(self, user, password):
        """ Logs the customer_user in and stores the session_id for subsequent
        requests.
        """
        self.session_id = self.session_create(
            password=password,
            customer_user_login=user)

    @authenticated
    def ticket_get(self, ticket_id, get_articles=False,
                   get_dynamic_fields=False,
                   get_attachments=False, *args, **kwargs):
        """ Get a ticket by id ; beware, TicketID != TicketNumber

        @param ticket_id : the TicketID of the ticket
        @param get_articles : grab articles linked to the ticket
        @param get_dynamic_fields : include dynamic fields in result
        @param get_attachments : include attachments in result

        @return a `Ticket`, Ticket.articles() will give articles if relevant.
        Ticket.articles()[i].attachments() will return the attachments for
        an article, wheres Ticket.articles()[i].save_attachments(<folderpath>)
        will save the attachments of article[i] to the specified folder.
        """
        params = {'TicketID' : str(ticket_id)}
        params.update(kwargs)
        if get_articles:
            params['AllArticles'] = True
        if get_dynamic_fields:
            params['DynamicFields'] = True
        if get_attachments:
            params['Attachments'] = True

        ret = self.req('TicketGet', **params)
        return Ticket.from_xml(self._unpack_resp_one(ret))

    @authenticated
    def ticket_search(self, dynamic_fields=None, **kwargs):
        """
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

    @authenticated
    def ticket_create(self, ticket, article, dynamic_fields=None,
                      attachments=None, **kwargs):
        """
        @param ticket a Ticket
        @param article an Article
        @param dynamic_fields a list of Dynamic Fields
        @param attachments a list of Attachments
        @returns the ticketID, TicketNumber
        """
        ticket_requirements = (
            ('StateID', 'State'),
            ('PriorityID', 'Priority'),
            ('QueueID', 'Queue'),
        )
        article_requirements = ('Subject', 'Body', 'Charset', 'MimeType')
        dynamic_field_requirements = ('Name', 'Value')
        attachment_field_requirements = ('Content','ContentType', 'Filename')
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


    @authenticated
    def ticket_update(self, ticket_id=None, ticket_number=None,
                      ticket=None, article=None,
                      dynamic_fields=None, **kwargs):
        """
        @param ticket_id the ticket ID of the ticket to modify
        @param ticket_number the ticket Number of the ticket to modify
        @param ticket a ticket containing the fields to change on ticket
        @param article a new Article to append to the ticket
        @param dynamic_fields a list of Dynamic Fields to change on ticket
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
            raise ValueError('requires at least one among ticket, article, dynamic_fields')
        else:
            if (ticket):
                kwargs['Ticket'] = ticket
            if (article):
                kwargs['Article'] = article
            if (dynamic_fields):
                kwargs['DynamicField'] = dynamic_fields

        ret = self.req('TicketUpdate', **kwargs)
        elements = self._unpack_resp_several(ret)
        infos = {extract_tagname(i): int(i.text) for i in elements}
        return infos['TicketID'], infos['TicketNumber']
