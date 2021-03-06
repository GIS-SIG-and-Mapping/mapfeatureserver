mapfeatureserver
================

WSGI (Python, Flask) service for ArcGIS Feature Layer REST replacement/implementation

## About

Mapfeatureserver is a web service written on Python (WSGI, Flask) and it can act like ArcGIS FeatureServer
([Feature Service Layer aka FeatureLayer](http://resources.arcgis.com/en/help/rest/apiref/fslayer.html))
without ArcGIS.

Here we have Proof Of Concept, a sketchy draft for evaluation of idea.

For now, service can serve two kind of requests:

1. layer metadata [http://&lt;featureservice-url&gt;/&lt;layerId&gt;](http://resources.arcgis.com/en/help/rest/apiref/fslayer.html)
2. layer data query by box [http://&lt;featurelayer-url&gt;/query](http://resources.arcgis.com/en/help/rest/apiref/fsquery.html)

For data query only subset of arguments be parsed.
E.g: `http://service/0/query?geometry={"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}&outSR=102100`

These two types of requests allow using service layers in web maps like
[Cartobonus](http://www.allgis.org/cartobonus/help/)
already. This web maps  builded using ArcGIS Silverlight API.
By word "using" I meant actions like "add layer to map", "view feature attributes" in popups and table.
Functions like records filtering, editing, updating and creating features will be availible later.
You can use MFS layers in other Esri API maybe, I didn't test.

## How to use

For starting a service you need to perform next steps:
* Download Mapfeatureserver and set suitable values for parameters in module `mapfeatureserver\wsgi\default_settings.py`
* Install Python 2.7 and libraries, e.g. for MS Windows

```
set path=%path%;c:\d\Python27;c:\d\Python27\Scripts
pip install Flask flask-login blinker psycopg2 simplejson
```

[psycopg2 for Windows](http://www.stickpeople.com/projects/python/win-psycopg/)

* Start Flask application

```
pushd mapfeatureserver\wsgi
python mapfs_controller.py
```

Service URL must be
`http://localhost:5000/`
Open that page in browser and you will see links to test layers, they shouldn't work. Remove those links by editing file
`mapfeatureserver\wsgi\templates\servlets.html`

If you want to create new layer, you need perform next steps:
* get access to PostGIS DB, for example by installing [PostGIS](http://postgis.net/windows_downloads) on your host;
* load some shape file (shp) to DB, like this:

```
set path=%path%;c:\Program Files\PostgreSQL\9.0\bin
pushd c:\t\shpdir
shp2pgsql.exe -d -I -s 4326 -W cp1251 flyzone.shp mfsdata.flyzone > flyzone.dump.sql
psql -f flyzone.dump.sql postgisdb mfs
```

* write layer info (layer ID - any integer, table name, etc) to config file
`mapfeatureserver\config\layers.config.ini`
along with PostgreSQL connection parameters. For help look example config records.

* Create layer meta data file
`mapfeatureserver\config\layer.<layer id>.config.json`
this is hardest thing to do. For help you can copy meta data from similar ArcGIS Feature Layer configured as you wish.
E.g. URL for that AGS layer should be like this
`http://testags/arcgis/rest/services/flyzone/FeatureServer/2?f=pjson`
if you have AGS web service named 'flyzone'.
Also, you should use special page from MFS, e.g.
`http://localhost:5000/admin/dsn/flyzone?oidfield=gid&geomfield=geom`

You can use created layer in web maps like [Cartobonus](http://www.allgis.org/cartobonus/help/)
or any other [ArcGIS style web maps](http://resources.arcgis.com/content/web/web-apis)
by adding it to map as regular ArcGIS FeatureLayer `http://hostname:5000/<layer id>`

### It's not working!

If you think that MFS didn't work properly, look to the window with Flask application.
If you see mapfs_controller.py traceback - you right, MFS is broken.
Copy that traceback and sent it to me or open an issue on GitHub.

Some tips

* PostgreSQL connection, user privileges.
A minimum set of privileges for user 'guest' should be not less than

```
CREATE USER guest WITH password 'guest';
ALTER USER guest SET search_path TO mfsdata,public;
GRANT USAGE ON schema mfsdata TO guest;
GRANT SELECT ON table mfsdata.patching TO guest;
GRANT SELECT ON geometry_columns TO guest;
GRANT SELECT ON geography_columns TO guest;
GRANT SELECT ON spatial_ref_sys TO guest;
```

according layer data in 'mfsdata.patching' table, for example.

## TODO

* Combine Python modules to package. Create MFS distribution (PyPI).
* Aliases for layer fields should be readed from layer meta data.
* Records filtering - [query 'where' clause](http://resources.arcgis.com/en/help/rest/apiref/fsquery.html).
* Edit function for features - [Add Features, Update Features, Delete Features, Apply Edits](http://resources.arcgis.com/en/help/rest/apiref/fslayer.html).
* Features fields list filtering - [query 'outFields' parameter](http://resources.arcgis.com/en/help/rest/apiref/fsquery.html).
* Source code unittesting and using mock instead of actual DB.
* Write adapters for layers in MySQL, MongoDB, WFS (Web Feature Service)
* User interface for loading shape files and creating layers.
* [Identify function](http://resources.arcgis.com/en/help/rest/apiref/identify.html) aka '????????' ?? ????????????????????.

## License and restrictions

Mapfeatureserver is free software: you can redistribute it and/or modify
it under the terms of the [GNU General Public License](http://www.gnu.org/licenses/gpl.html) as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Restrictions: for this release you need access to PostGIS DB;
you have to create layer meta data file by hand;
from Esri specs only one type of query realized - select features by box.

## Links

* [???????????? ???? GIS-Lab](http://wiki.gis-lab.info/w/Mapfeatureserver_??????_????????????_ArcGIS_Server)
* [???????????????????? ???????????? ???? ???????????? ??????-??????](http://gis-lab.info/forum/viewtopic.php?f=3&t=13731)
* [???????????? ?? ?????????? ????????????](http://vasnake.blogspot.ru/2013/05/mapfeatureserver-poc.html)
* [ArcGIS Server REST API](http://resources.arcgis.com/en/help/rest/apiref/fslayer.html)
* [ArcGIS Server REST API - Layer (Feature Service)](http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000w6000000)
* Mapfeatureserver client - [web map viewer Cartobonus](http://www.allgis.org/cartobonus/help/)
* Brothers in arms: [Papyrus](http://papyrus.readthedocs.org/en/latest/), [FeatureServer](http://featureserver.org/)

Copyright 2012-2013 Valentin Fedulov
mailto:vasnake@gmail.com
