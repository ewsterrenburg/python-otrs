from .operations import LanguageList,PublicCategoryList,PublicFAQGet,PublicFAQSearch
from ..client import WebService

def GenericFAQConnectorSOAP(webservice_name='GenericFAQConnectorSOAP'):
    return WebService(webservice_name, 'http://www.otrs.org/FAQConnector', LanguageList=LanguageList(),PublicCategoryList=PublicCategoryList(),PublicFAQGet=PublicFAQGet(),PublicFAQSearch=PublicFAQSearch())
