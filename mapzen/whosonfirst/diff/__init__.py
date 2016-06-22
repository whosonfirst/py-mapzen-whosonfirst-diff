# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import subprocess
import logging
import geojson
import os
import json
import hashlib

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

        If maybe I had even the vaguest of ideas what this error message even
        meant we might try using this but as it is... (20160122/thisisaaronland)

        diff = json_delta.udiff(previous, current)

        Traceback (most recent call previous):
        File "./__init__.py", line 33, in <module>
        d.compare(101736545)
        File "./__init__.py", line 27, in compare
        diff = json_delta.udiff(previous, current)
        File "build/bdist.linux-x86_64/egg/json_delta/_udiff.py", line 92, in udiff
        File "build/bdist.linux-x86_64/egg/json_delta/_diff.py", line 72, in diff
        File "build/bdist.linux-x86_64/egg/json_delta/_diff.py", line 128, in needle_diff
        File "build/bdist.linux-x86_64/egg/json_delta/_diff.py", line 299, in keyset_diff
        File "build/bdist.linux-x86_64/egg/json_delta/_diff.py", line 269, in compute_keysets
        AssertionError: {"bbox": [-73.97435119999994, 45.40965310900003, -73.47412679299993, 
        """

        changes = {}

        changes['geom'] = self.compare_geom(previous, current)

        # https://github.com/whosonfirst/py-mapzen-whosonfirst-diff/issues/2

        changes['tbah'] = self.touched_by_a_human(previous, current)

        if len(changes['tbah'].keys()) > 0:
            changes['is_tbah'] = True
        else:
            changes['is_tbah'] = False

        #

        previous_props = previous.get('properties', {})
        current_props = current.get('properties', {})
        changes['properties'] = self.compare_object(previous_props, current_props)

        #

        wof = {
            'concordances': {},
            'hierarchy': [],
            'supersedes': [],
            'superseded_by': []
        }

        for k, v in wof.items():

            wof_k = "wof:%s" % k

            previous_el = previous_props.get(wof_k, {})
            current_el = current_props.get(wof_k, {})

            changes[k] = self.compare_object(previous_el, current_el)

        #

        return changes

    def compare_geom(self, left, right):

        left_hash = mapzen.whosonfirst.utils.hash_geom(left)
        right_hash = mapzen.whosonfirst.utils.hash_geom(right)

        return left_hash != right_hash

    def compare_object_itemized(self, left, right):
        # please write me...
        pass

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
        return {}

if __name__ == '__main__':

    import pprint

    d = diff()
    print pprint.pformat(d.compare(85922583))
