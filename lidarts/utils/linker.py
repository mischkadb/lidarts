from six.moves.urllib.parse import urlparse
from bleach.linkifier import Linker


def set_target(attrs, new=False):
    p = urlparse(attrs[(None, 'href')])
    if p.netloc not in ['lidarts.org']:
        attrs[(None, 'target')] = '_blank'
        attrs[(None, 'class')] = 'external'
    else:
        attrs.pop((None, 'target'), None)
    return attrs


linker = Linker(callbacks=[set_target])
