"""OTRS :: faq :: template."""
from otrs.client import WebService
from otrs.faq.operations import LanguageList
from otrs.faq.operations import PublicCategoryList
from otrs.faq.operations import PublicFAQGet
from otrs.faq.operations import PublicFAQSearch


def GenericFAQConnectorSOAP(webservice_name='GenericFAQConnectorSOAP'):
    """Return a GenericFAQConnectorSOAP Webservice object.

    @returns a WebService object with the GenericFAQConnectorSOAP operations
    """
    return WebService(webservice_name, 'http://www.otrs.org/FAQConnector',
                      LanguageList=LanguageList(),
                      PublicCategoryList=PublicCategoryList(),
                      PublicFAQGet=PublicFAQGet(),
                      PublicFAQSearch=PublicFAQSearch())
