""" FAQ:: Operations

"""

from .objects import Category as CategoryObject, Language as LanguageObject, FAQItem as FAQItemObject
from ..client import OperationBase, authenticated
from ..objects import extract_tagname

class FAQ(OperationBase):

    """ Base class for OTRS FAQ:: operations

    """

class LanguageList(FAQ):
    """ Class to handle OTRS ITSM FAQ::LanguageList operation

    """

    @authenticated
    def __call__(self, *args, **kwargs):
        """ Returns the Language List from FAQ

        @returns list of languages
        """

        ret = self.req('LanguageList', **kwargs)
        elements = self._unpack_resp_several(ret)
        return [LanguageObject.from_xml(language) for language in elements]



class PublicCategoryList(FAQ):
    """ Class to handle OTRS ITSM FAQ::PublicCategoryList operation

    """

    @authenticated
    def __call__(self, **kwargs):
        """ Returns the Public Category List from FAQ

        @returns list of category objects
        """

        ret = self.req('PublicCategoryList', **kwargs)
        elements = self._unpack_resp_several(ret)
        return [CategoryObject.from_xml(category) for category in elements]



class PublicFAQGet(FAQ):
    """ Class to handle OTRS ITSM FAQ::PublicFAQGet operation

    """

    @authenticated
    def __call__(self, item_id, get_attachments=False, **kwargs):
        """ Get a public FAQItem by id

        @param item_id : the ItemID of the public FAQItem
                               NOTE: ItemID != FAQ Number

        @return an `FAQItem`
        """
        params = {'ItemID': str(item_id)}
        params.update(kwargs)
        if get_attachments:
            params['GetAttachmentContents'] = 1
        else:
            params['GetAttachmentContents'] = 0

        ret = self.req('PublicFAQGet', **params)
        return FAQItemObject.from_xml(self._unpack_resp_one(ret))

class PublicFAQSearch(FAQ):
    """ Class to handle OTRS ITSM FAQ::PublicFAQSearch operation

    """

    @authenticated
    def __call__(self, *args, **kwargs):
        """
        @returns a list of matching public FAQItem IDs
        """

        ret = self.req('PublicFAQSearch', **kwargs)
        return [int(i.text) for i in self._unpack_resp_several(ret)]
