# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import subprocess
import logging
import geojson
import os
import json
import hashlib

import datetime

import deepdiff

import mapzen.whosonfirst.utils

class compare:

    def __init__(self, **kwargs):

        source = kwargs.get('source', None)

        self.source = source

    def report(self, id, steps=1):

        data = os.path.join(self.source, "data")
        data = (data,)

        current = mapzen.whosonfirst.utils.load(data, id)

        rel_path = mapzen.whosonfirst.utils.id2relpath(id)

        targets = [
            "HEAD~%d:data/%s" % (steps, rel_path),
            "HEAD:data/%s" % rel_path
        ]

        out = None

        for target in targets:

            cmd = [ "git", "-C", self.source, "show", target ]
            logging.debug(cmd)

            try:
                _out = subprocess.check_output(cmd)

                out = _out
                break

            except Exception, e:
                logging.warning("failed generate report for %s, because %s" % (rel_path, e))

        if not out:
            raise Exception, "Failed to generate a report for %s (using HEAD~1 and HEAD)" % rel_path
            
        previous = geojson.loads(out)

        """
        wof-diff -s /usr/local/data/whosonfirst-data/ 102147495
        {'dic_item_added': set([u"root['properties']['mz:hierarchy_label']",
                                u"root['properties']['wof:repo']"]),
         'values_changed': {u"root['properties']['wof:lastmodified']": {'newvalue': 1466610665,
                                                                        'oldvalue': 1459361729}}}
        """

        diff = deepdiff.DeepDiff(previous, current)

        # import pprint
        # print pprint.pformat(diff)
        # print dir(diff)

        report = {
            'details': str(diff),	# see the str-ification / DeepDiff objects are not JSON-serializable which is sad...
            'geom': False,
            'concordances': False,
            'hierarchy': False,
            'supersedes': False,
            'superseded_by': False,
        }

        changed_key = {
            "geom": "root['geometry']",
            "concordances": "root['properties']['wof:concordances']",
            "hierarchy": "root['properties']['wof:hierarchy']",
            "supersedes": "root['properties']['wof:supersedes']",
            "superseded_by": "root['properties']['wof:superseded_by']",
        }

        changed = diff['values_changed']

        for k, v in changed_key.items():

            if changed.get(v, False):
                report[k] = changed[v]

        # https://github.com/whosonfirst/py-mapzen-whosonfirst-diff/issues/2

        report['tbah'] = self.touched_by_a_human(previous, current)
        
        if len(report['tbah'].keys()) > 0:
            report['is_tbah'] = True
        else:
            report['is_tbah'] = False

        print pprint.pformat(report)
        return report

    def compare_geom(self, left, right):

        left_hash = mapzen.whosonfirst.utils.hash_geom(left)
        right_hash = mapzen.whosonfirst.utils.hash_geom(right)

        return left_hash != right_hash

    def compare_object(self, left_obj, right_obj):

        left_hash = self.hash_obj(left_obj)
        right_hash = self.hash_obj(right_obj)

        return left_hash != right_hash

    # put this in utils? probably...

    def hash_obj(self, obj):

        str_obj = json.dumps(obj)

        hash = hashlib.md5()
        hash.update(str_obj)
        return hash.hexdigest()

    # work in progress
    # https://github.com/whosonfirst/py-mapzen-whosonfirst-diff/issues/3

    def touched_by_a_human(self, previous, current):

        tbah = []

        previous_props = previous.get('properties', {})
        current_props = current.get('properties', {})

        return {}

if __name__ == '__main__':

    import pprint

    d = diff()
    print pprint.pformat(d.compare(85922583))
