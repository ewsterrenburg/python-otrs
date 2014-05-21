class OTRSObject(object):
    def __init__(self, *args, **kwargs):
        self.attrs = kwargs

    def __getattr__(self, k):
        return autocast(self.attrs[k])

    @classmethod
    def from_xml(cls, xml_element):
        if not xml_element.tag.endswith(cls.XML_NAME):
            raise ValueError(
                'xml_element should be a {} node, not {}'.format(
                    cls.XML_NAME, xml_element.tag))
        attrs = {extract_tagname(t): t.text for t in xml_element.getchildren()}

        return cls(**attrs)

    def check_fields(self, fields):
        keys = self.attrs.keys()
        for i in fields:
            if isinstance(i, (tuple, list)):
                valid = self.attrs.has_key(i[0]) or self.attrs.has_key(i[1])
            else:
                valid = self.attrs.has_key(i[0])
            if not valid:
                raise ValueError('{} should be filled'.format(i))


def extract_tagname(element):
    qualified_name = element.tag
    try:
        return qualified_name.split('}')[1]
    except IndexError:
        # if it's not namespaced, then return the tag name itself
        return element.tag
        #raise ValueError('"{}" is not a tag name'.format(qualified_name))

def autocast(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

class Ticket(OTRSObject):
    XML_NAME = 'Ticket'

class Article(OTRSObject):
    XML_NAME = 'Article'
