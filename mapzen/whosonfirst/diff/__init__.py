import subprocess
import logging
import geojson
import os
import json
import hashlib
import re

# https://github.com/seperman/deepdiff
# http://zepworks.com/blog/diff-it-to-digg-it/
# https://deepdiff.readthedocs.io/en/latest/

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

        diff = self.diff(previous, current)

        report = {
            'details': diff,
            'geom': False,
            'concordances': False,
            'hierarchy': False,
            'supersedes': False,
            'superseded_by': False,
            'tbah': False,
            'tbah_properties': []
        }

        changed_key = {
            "geom": "root['geometry']",
            "concordances": "root['properties']['wof:concordances']",
            "hierarchy": "root['properties']['wof:hierarchy']",
            "supersedes": "root['properties']['wof:supersedes']",
            "superseded_by": "root['properties']['wof:superseded_by']",
        }

        # THINGS THAT HAVE CHANGED

        """
        "values_changed": {
        	"root['properties']['wof:lastmodified']": {
        		"newvalue": 1466619352, 
        		"oldvalue": 1459361729
        	}
        }
        """

        changed = diff['values_changed']

        for k, v in changed_key.items():

            if changed.get(v, False):
                report[k] = True

        # THINGS THAT HAVE BEEN ADDED

        """
        "dic_item_added": [
        	"root['properties']['mz:hierarchy_label']", 
        	"root['properties']['wof:concordances']['foo:bar']", 
        	"root['properties']['wof:repo']"
        ]
        """

        for a in diff['dic_item_added']:

            for k, v in changed_key.items():

                if a.startswith(v):
                    report[k] = True
                    break

        # TO DO - THINGS THAT HAVE BEEN REMOVED
        # https://github.com/whosonfirst/py-mapzen-whosonfirst-diff/issues/5

        # https://github.com/whosonfirst/py-mapzen-whosonfirst-diff/issues/1

        ignorable_properties = [
            'wof:created',
            'wof:lastmodified',
        ]

        tbah_properties = []
        tbah_check = []

        # Honestly, we could just update the 'replace' command below to
        # remove "root['properties']" but whatever... (20160622/thisisaaronland)

        previous_props = previous['properties']
        current_props = current['properties']

        diff = self.diff(previous_props, current_props)

        tbah_check.extend(diff['values_changed'].keys())
        tbah_check.extend(diff['dic_item_added'])

        #

        p = re.compile("(?:\[(?:'([^\']+)'|(\d+))\])")

        for k in tbah_check:

            k = k.replace("root", "")

            dot_k = []
            dot_k_str = ""

            ignore = False

            for m in re.findall(p, k):

                dict_key, list_index = m	# one of these will be ''

                if dict_key != '':
                    dot_k.append(dict_key)
                else:
                    dot_k.append(list_index)	# do we want some other syntax than "a number" ?
                
                dot_k_str = ".".join(dot_k)

                if dot_k_str in ignorable_properties:
                    ignore = True
                    break

            if ignore:
                continue

            tbah_properties.append(dot_k_str)

        if len(tbah_properties) > 0:

            report['tbah'] = True
            report['tbah_properties'] = tbah_properties

        return report

    # deprecated ?

    def compare_geom(self, left, right):

        left_hash = mapzen.whosonfirst.utils.hash_geom(left)
        right_hash = mapzen.whosonfirst.utils.hash_geom(right)

        return left_hash != right_hash

    # deprecated ?

    def compare_object(self, left_obj, right_obj):

        left_hash = self.hash_obj(left_obj)
        right_hash = self.hash_obj(right_obj)

        return left_hash != right_hash

    # deprecated ?

    def hash_obj(self, obj):

        str_obj = json.dumps(obj)

        hash = hashlib.md5()
        hash.update(str_obj)
        return hash.hexdigest()

    def diff(self, previous, current):

        # This is all so that we can serialize the diff response as JSON
        # (20160622/thisisaaronland)

        # grrnrnnrnrnnnnrnnhhnnnn - for some reason we can't just type(v) == types.SetType
        # https://github.com/seperman/deepdiff/blob/master/deepdiff/deepdiff.py#L274

        isa_set = [
            'dic_item_added',
            'attribute_added',
            'attribute_removed',
            'set_item_removed',
            'set_item_added',
        ]

        diff = deepdiff.DeepDiff(previous, current)

        for k, v in diff.items():

            if k in isa_set:
                diff[k] = list(v)

        return diff

if __name__ == '__main__':

    import pprint

    d = diff()
    print pprint.pformat(d.compare(85922583))
