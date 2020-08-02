import os
import sys

import pytest
import msgpack

import reproducible


here = os.path.dirname(__file__)

def save_msgpack_xz(data, filename):
    print(sys.version_info < (3, 5))
    import lzma
    if not filename.endswith('.msgpack.xz'):
        filename += '.msgpack.xz'
    with lzma.open(filename, mode='wb') as fd:
        def default(o):
            """This keeps the distinction between tuples and lists."""
            if isinstance(o, tuple):
                return {
                    '__type__': 'tuple',
                    'value': list(o),
                    }
            raise TypeError(repr(o))

        msgpack_data = msgpack.packb(data, strict_types=True, default=default)
        fd.write(msgpack_data)
    return filename

def load_msgpack_xz(filename):
    import lzma
    if not os.path.isfile(filename):
        # trying with appending the extention
        filename += '.msgpack.xz'

    with lzma.open(filename, mode='rb') as fd:
        msgpack_data = fd.read()

    def convert(o):
        """Restore tuples (instead of lists)"""
        if o.get('__type__') == 'tuple':
            return tuple(o['value'])
        return o

    return msgpack.unpackb(msgpack_data, raw=False, object_hook=convert)

@pytest.mark.skipif(sys.version_info < (3, 5), reason="lzma not in python 2.7")
def test_msgpack():
    context = reproducible.Context(cpuinfo=True)
    save_msgpack_xz(context.data, os.path.join(here, 'data.msgpack.xz'))


if __name__ == '__main__':
    test_msgpack()
