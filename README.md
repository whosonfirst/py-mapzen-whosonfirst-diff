# py-mapzen-whosonfirst-diff

Python library for describing changes between versions of a Who\'s On First document.

This is *not* a full-featured diff tool. It may become one over time but for the time being it is meant to compare a "most-recent"  Who's On First document with the last version commited to Git and to generate enough information to determine whether any related tasks need to be triggered (for example rebuilding the concordances list).

## Caveats

This is probably not ready for you to use yet. No.

## But if you're feeling lucky

### From the command line:

```
$> ./scripts/wof-diff -s /usr/local/mapzen/whosonfirst-data 85922583 
{
  "concordances": false, 
  "hierarchy": false, 
  "superseded_by": false, 
  "supersedes": false, 
  "geom": false, 
  "properties": true
}
```

### From your code:

```
import mapzen.whosonfirst.diff

source = "/usr/local/mapzen/whosonfirst-data"
diff = mapzen.whosonfirst.diff.compare(source=source)
report = diff.report(85922583)
```

