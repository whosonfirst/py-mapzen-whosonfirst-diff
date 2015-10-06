# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import difflib
import mapzen.whosonfirst.utils
import mapzen.whosonfirst.geojson

import StringIO

class feature:

    def __init__(self, old, new):
        self.old = old
        self.new = new

        self.encoder = mapzen.whosonfirst.geojson.encoder()

    def udiff(self):

        old = StringIO.StringIO()
        self.encoder.encode_feature(self.old, old)
        old.seek(0)

        new = StringIO.StringIO()
        self.encoder.encode_feature(self.new, new)
        new.seek(0)

        return difflib.unified_diff(old.readline(), new.readlines())

class diff:

    def __init__(self, source):
        self.source = source

    def compare(self, new):

        props = new['properties']
        wofid = props.get('wof:id')

        old = mapzen.whosonfirst.utils.load(self.source, wofid)
        return feature(old, new)

if __name__ == '__main__':

    source = '/usr/local/mapzen/whosonfirst-data/data'
    id = 101736545

    d = diff(source)
    f = mapzen.whosonfirst.utils.load(source, id)

    f['properties']['debug:wub'] = 'wub wub'
    c = d.compare(f)

    iter = c.udiff()

    for ln in iter:
        print ln
