"""OTRS :: faq :: template."""
from otrs.faq.operations import LanguageList, PublicCategoryList
from otrs.faq.operations import PublicFAQGet, PublicFAQSearch
from otrs.client import WebService

def GenericFAQConnectorSOAP(webservice_name='GenericFAQConnectorSOAP'):
    """Return a GenericFAQConnectorSOAP Webservice object.

    @returns a WebService object with the GenericFAQConnectorSOAP operations
    """
    return WebService(webservice_name, 'http://www.otrs.org/FAQConnector',
                      LanguageList=LanguageList(),
                      PublicCategoryList=PublicCategoryList(),
                      PublicFAQGet=PublicFAQGet(),
                      PublicFAQSearch=PublicFAQSearch())
