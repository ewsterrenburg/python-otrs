try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
from posixpath import join as urljoin
import xml.etree.ElementTree as etree
from .objects import OTRSObject, extract_tagname
import codecs
import sys
import abc

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
               query on a dynamic field: `Equals`, `Like`, `GreaterThan`,
               `GreaterThanEquals`, `SmallerThan`  or `SmallerThanEquals`.
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

        return func(self, *args, **kwargs)

    return add_auth

class OperationBase(object):
    """ Base class for OTRS operations

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, opName):
        self.operName = opName # otrs connector operation name
        self.wsObject = None   # web services object this operation belongs to

    def __init__(self):
        self.operName = type(self).__name__ # otrs connector operation name
        self.wsObject  = None # web services object this operation belongs to

    def getWebServiceObjectAttribute(self, attribName):
        return getattr(self.wsObject, attribName)

    def getClientObjectAttribute(self, attribName):
        return self.wsObject.getClientObjectAttribute(attribName)

    def setClientObjectAttribute(self, attribName, attribValue):
        self.wsObject.setClientObjectAttribute(attribName, attribValue)

    @abc.abstractmethod
    def __call__(self):
        return

    @property
    def endpoint(self):
        return self.getWebServiceObjectAttribute('endpoint')

    @property
    def login(self):
        return self.getClientObjectAttribute('login')

    @property
    def password(self):
        return self.getClientObjectAttribute('password')

    @property
    def session_id(self):
        return self.getClientObjectAttribute('session_id')

    @session_id.setter
    def session_id(self, sessionid):
        self.setClientObjectAttribute('session_id', sessionid)

    @property
    def soap_envelope(self):
        return '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns= "' + self.getWebServiceObjectAttribute('wsNamespace') + '"><soapenv:Header/><soapenv:Body>{}</soapenv:Body></soapenv:Envelope>'

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

        for k, v in kwargs.items():
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
            {'Content-Type': 'text/xml;charset=utf-8'})

        if (sys.version_info[0] == 3 and sys.version_info < (3,4,3)) or sys.version_info < (2,7,9):
            fd = urllib2.urlopen(request)
        else:
            fd = urllib2.urlopen(request, context=self.ssl_context)

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
                print('-' * 80)
                print(s)
                print('-' * 80)
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

    def _pack_req(self, element):
        """
        @param element : a etree.Element
        @returns       : a string, wrapping element within the request tags

        """
        return self.soap_envelope.format(codecs.decode(etree.tostring(element),'utf-8')).encode('utf-8')

class WebService(object):
    """ Base class for OTRS Web Service

    """

    def __init__(self, wsName, wsNamespace, **kwargs):
        self.clientObject = None # link to parent client object
        self.wsName = wsName     # name for OTRS web service
        self.wsNamespace = wsNamespace # OTRS namespace url

        # add all variables in kwargs into the local dictionary
        self.__dict__.update(kwargs)

        # for operations, set backlinks to their associated webservice
        for arg in kwargs:
            if isinstance(getattr(self, arg), OperationBase):
                getattr(self, arg).wsObject = self
                # if attribute is type OperationBase, set backlink to WebService

        # set defaults if attributes are not present
        if not hasattr(self, 'wsRequestNameScheme'):
            self.wsRequestNameScheme = '<FunctionName>DATA</FunctionName>'
        if not hasattr(self, 'wsResponseNameScheme'):
            self.wsResponseNameScheme = '<FunctionNameResponse>DATA</FunctionNameResponse>'

    def getClientObjectAttribute(self, attribName):
        return getattr(self.clientObject,attribName)

    def setClientObjectAttribute(self, attribName, attribValue):
        setattr(self.clientObject,attribName,attribValue)

    @property
    def endpoint(self):
        return urljoin(self.getClientObjectAttribute('giurl'),self.wsName)


class GenericInterfaceClient(object):
    """ Client for the OTRS Generic Interface

    """

    def __init__(self, server, **kwargs):
        """ @param server : the http(s) URL of the root installation of OTRS
                            (e.g: https://tickets.example.net)
        """

        # add all variables in kwargs into the local dictionary
        self.__dict__.update(kwargs)

        # for webservices attached to this client object, backlink them
        # to this client object to allow access to session login/password

        for arg in kwargs:
             if isinstance(getattr(self, arg), WebService):
                getattr(self, arg).clientObject = self # set backlink for web services to this obj
        self.login = None
        self.password = None
        self.session_id = None
        self.giurl = urljoin(
            server, 'otrs/nph-genericinterface.pl/Webservice/')

    def register_credentials(self, login, password):
        """ Save the identifiers in memory, they will be used with each
            subsequent request requiring authentication
        """
        self.login = login
        self.password = password

class OldGTCClass(GenericInterfaceClient):
    """ Old deprecated generic ticket connector class, used for
        backward compatibility with previous versions. All
        methods in here are deprecated
    """

    def session_create(self, password, user_login=None,
                                       customer_user_login=None):
        """ DEPRECATED - Logs the user or customeruser in

        @returns the session_id
        """
        self.tc.SessionCreate(password,user_login=user_login,customer_user_login=customer_user_login)

    def user_session_register(self, user, password):
        """ Logs the user in and stores the session_id for subsequent requests
            DEPRECATED
        """
        self.session_create(
            password=password,
            user_login=user)

    def customer_user_session_register(self, user, password):
        """ Logs the customer_user in and stores the session_id for subsequent
        requests. DEPRECATED
        """
        self.session_create(
            password=password,
            customer_user_login=user)

    @authenticated
    def ticket_create(self, ticket, article, dynamic_fields=None,
                      attachments=None, **kwargs):
        # ticket_create is deprecated, for backward compat, calls new method
        return self.tc.TicketCreate(ticket, article, dynamic_fields=dynamic_fields, attachments=attachments, **kwargs)

    @authenticated
    def ticket_get(self, ticket_id, get_articles=False, get_dynamic_fields=False, get_attachments=False, *args, **kwargs):
        # ticket_get is deprecated, for backward compat, calls new method
        return self.tc.TicketGet(ticket_id, get_articles=get_articles, get_dynamic_fields=get_dynamic_fields, get_attachments=get_attachments, *args, **kwargs)

    @authenticated
    def ticket_search(self, dynamic_fields=None, **kwargs):
        # ticket_search is deprecated, for backward compat, calls new method
        return self.tc.TicketSearch(dynamic_fields=dynamic_fields, **kwargs)

    @authenticated
    def ticket_update(self, ticket_id=None, ticket_number=None,
                      ticket=None, article=None, dynamic_fields=None,
                      attachments=None, **kwargs):
        # ticket_update is deprecated, for backward compat, calls new method
        return self.tc.TicketUpdate(ticket_id=ticket_id, ticket_number=ticket_number,
                      ticket=ticket, article=article, dynamic_fields=dynamic_fields,
                      attachments=attachments, **kwargs)

def GenericTicketConnector(server, webservice_name='GenericTicketConnector', ssl_context=None):
    """ DEPRECATED, ONLY HERE FOR BACKWARD COMPATIBILITY """
    from ticket.operations import SessionCreate,TicketCreate,TicketGet,TicketSearch,TicketUpdate
    ticketconnector = WebService(webservice_name, 'http://www.otrs.org/TicketConnector', ssl_context=ssl_context, SessionCreate=SessionCreate(),TicketCreate=TicketCreate(),TicketGet=TicketGet(),TicketSearch=TicketSearch(),TicketUpdate=TicketUpdate())
    return OldGTCClass(server,tc=ticketconnector)
