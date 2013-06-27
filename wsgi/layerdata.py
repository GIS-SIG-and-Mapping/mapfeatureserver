#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

r""" Map Feature Server module.
Free featureserver realization for API
http://resources.arcgis.com/en/help/rest/apiref/fslayer.html

Copyright 2012-2013 Valentin Fedulov

This file is part of Mapfeatureserver.

Mapfeatureserver is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Mapfeatureserver is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Mapfeatureserver.  If not, see <http://www.gnu.org/licenses/>.
"""

import postgis, esri
import layermeta

CP = 'UTF-8'


def layerData(lyrconf, datasource, operation):
    """ Return dictionary with layer data in response to query
    according to operations for Feature Service Layer
    http://resources.arcgis.com/en/help/rest/apiref/fslayer.html
    http://resources.arcgis.com/en/help/rest/apiref/fsquery.html#response

    example http://vags101.algis.com/arcgis/rest/services/PATHING/FeatureServer/0/query?returnGeometry=true&geometryType=esriGeometryEnvelope&geometry={%22xmin%22%3a-7182265.21424325%2c%22ymin%22%3a-1567516.84684806%2c%22xmax%22%3a17864620.2142433%2c%22ymax%22%3a14321601.0968481%2c%22spatialReference%22%3a{%22wkid%22%3a102100}}&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson

    Args:
        lyrconf: layermeta.LayerInfo object with all layer metadata;
        datasource: IDataSource implementation;
        operation: AGLayerOperation object, like AGLayerOpQuery with all operation parameters.

    Returns:
        A dict specified in http://resources.arcgis.com/en/help/rest/apiref/fsquery.html#response

    Raises:
        TypeError: if operation is not 'query' or datasource is not postgis.DataSource
        or query parameters doesn't meet realized subset of API.
    """
    #if 0: # hint for autocomplete. pydev can use this: assert isinstance(lyrconf, layermeta.LayerInfo)
    #   lyrconf = layermeta.LayerInfo()
    #   datasource = postgis.DataSource('')
    #   operation = esri.AGLayerOpQuery('')
    #assert isinstance(operation, esri.AGLayerOpQuery)
    assert isinstance(lyrconf, layermeta.LayerInfo)

    if isinstance(operation, esri.AGLayerOpQuery):
        #spatialReference - из параметра «outSR=102100» запроса
        # spatial filter multipolygon or box: '{"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}'
        spatFltParams = esri.SpatialFilterParams(operation.outSR, operation.geometry,
                                                 operation.geomType, operation.spatRelation)
        if not spatFltParams.isAllSet():
            raise TypeError("'geometry' parameter is invalid, must be (geometryType, geometry) at least.")

        if isinstance(datasource, postgis.DataSource):
            res = layerDataFilterByGeom(datasource, lyrconf, spatFltParams)
        else:
            raise TypeError('Unknown datasource')

    else:
        raise TypeError('Unsupported layer operation')

    #resJson = json.dumps(res, ensure_ascii=False, sort_keys=True, indent=2)
    return res
#def layerData(lyrconf, datasource, operation):


def layerDataFilterByGeom(datasource, lyrinfo, spatfilter):
    """ Return layer data from DB. Output formed as dictionary according to Esri spec.
    Features will be spatially filtered by inpGeom.

    spes:
        http://resources.arcgis.com/en/help/rest/apiref/fsquery.html
        http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Query_Feature_Service_Layer/02r3000000r1000000/

    example:
        http://vags101.algis.com/arcgis/rest/services/PATHING/FeatureServer/0/query?returnGeometry=true&geometryType=esriGeometryEnvelope&geometry={%22xmin%22%3a-7182265.21424325%2c%22ymin%22%3a-1567516.84684806%2c%22xmax%22%3a17864620.2142433%2c%22ymax%22%3a14321601.0968481%2c%22spatialReference%22%3a{%22wkid%22%3a102100}}&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson
        http://vdesk.algis.com:5000/3/query?returnGeometry=true&geometryType=esriGeometryPolygon&geometry=%7b%22spatialReference%22%3a%7b%22wkid%22%3a102100%7d%2c%22rings%22%3a%5b%5b%5b-3580921.90110393%2c-273950.309374072%5d%2c%5b-3580921.90110393%2c15615167.6343221%5d%2c%5b20037508.3427892%2c15615167.6343221%5d%2c%5b20037508.3427892%2c-273950.309374072%5d%2c%5b-3580921.90110393%2c-273950.309374072%5d%5d%2c%5b%5b-20037508.3427892%2c-273950.309374072%5d%2c%5b-20037508.3427892%2c15615167.6343221%5d%2c%5b-18609053.1581958%2c15615167.6343221%5d%2c%5b-18609053.1581958%2c-273950.309374072%5d%2c%5b-20037508.3427892%2c-273950.309374072%5d%5d%5d%7d&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=json&_ts=635056144548740692&

    Args:
        datasource: postgis.DataSource object;
        lyrinfo: layermeta.LayerInfo object with
            LayerInfo.tabname: layer table name;
            LayerInfo.geomfield: name for table field with geometry;
            LayerInfo.oidfield: name for field with OBJECTID;
        spatfilter: esri.SpatialFilterParams with filter data gathered from query:
            outSR: integer from request, e.g. 'outSR=102100' which is srid for projecting DB geometry data to;
            agsGeom: json string, filter geometry object from request e.g.
            'geometry={"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}'
            geomType: string, input geometry type, one of (esriGeometryEnvelope, esriGeometryPolygon)
            spatRel: string, spatial relation for filter, one of (esriSpatialRelIntersects)
    """
    assert isinstance(spatfilter, esri.SpatialFilterParams)
    inpGeomSR, inpGeomWKT = esri.AGGeoJSON2WKT(spatfilter.agsGeom, spatfilter.geomType)
    spatfilter = esri.OGCSpatialFilterParams(spatfilter, inpGeomSR, inpGeomWKT)

    assert isinstance(lyrinfo, layermeta.LayerInfo)
    if not spatfilter.outSR:
        spatfilter.outSR = lyrinfo.spatRefWKID

    if isinstance(datasource, postgis.DataSource):
        return datasource.filterLayerDataByGeom(lyrinfo, spatfilter)
    else:
        raise TypeError("Only PostGIS datasource availible, '%s' not supported yet" % type(datasource))
#def layerDataFilterByGeom(datasource, lyrconf, outSR, inpGeom, inpGeomType, spatRel):


def layerDataInBox(cur, lyrinfo, outSR, inpBox):
    """ Obsolete.
    Return layer data from DB as dictionary formed by Esri spec.
    Features will be spatially filtered by inpBox.

    spes:
        http://resources.arcgis.com/en/help/rest/apiref/fsquery.html
        http://resources.arcgis.com/en/help/rest/apiref/fslayer.html

    example:
        http://vags101.algis.com/arcgis/rest/services/PATHING/FeatureServer/0/query?returnGeometry=true&geometryType=esriGeometryEnvelope&geometry={%22xmin%22%3a-7182265.21424325%2c%22ymin%22%3a-1567516.84684806%2c%22xmax%22%3a17864620.2142433%2c%22ymax%22%3a14321601.0968481%2c%22spatialReference%22%3a{%22wkid%22%3a102100}}&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson

    Args:
        cur: PostGIS DB connection.cursor;
        lyrinfo: LayerInfoDB object with
            LayerInfo.tabname: layer table name;
            LayerInfo.geomfield: name for table field with geometry;
            LayerInfo.oidfield: name for field with OBJECTID;
        outSR: integer from request 'outSR=102100' is srid for projecting geometry data;
        inpBox: geometry object as json from request 'geometry={"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}'

    Hardcoded args:
        reference query had additional parameters:
            returnGeometry=true
            &geometryType=esriGeometryEnvelope
            &inSR=102100
            &spatialRel=esriSpatialRelIntersects
            &outFields=*
            &f=json
    """
    # srid for projecting data to
    outSrid = postgis.postgisSRID(outSR)

    # box for spatial filter
    box = esri.AGGeometryBox(inpBox)

    # output "spatialReference": ...
    spatialReference = {"wkid": int(outSR), "latestWkid": outSrid}

    # sql query
    sql = postgis.sqlSelectAllByBox(lyrinfo, outSrid, box)
#    print sql
    cur.execute(sql)
    if cur.rowcount is None or cur.rowcount <= 0:
        queryRes = {"objectIdFieldName": lyrinfo.oidfield, "globalIdFieldName": "", "features": []}
    else:
        #output "fields": [ { "name": "descr",   "alias": "Описание",   "type": "esriFieldTypeString",   "length": 100 },...
        #  из описания курсора «for rec in cur.description:»
        fields = postgis.attrFieldsFromDescr(cur, lyrinfo)

        #"geometryType": "esriGeometryPoint",   - из первой же записи выборки, поле «shape»
        #"features": [   { "attributes": {...,   "geometry": {...   - из результатов запроса.
        geometryType, features = postgis.featuresFromCursor(cur)

        queryRes = {"objectIdFieldName": lyrinfo.oidfield, "globalIdFieldName": "", "geometryType": geometryType,
            "spatialReference": spatialReference, "fields": fields, "features": features}
        if cur.rowcount >= 1000:
            queryRes["exceededTransferLimit"] = True

    return queryRes
#def layerDataInBox(cur, tabname, geomfield, oidfield, outSR, inpBox):


def tests():
    """ Doctests here.
    Unittests in test\test.py
    """
    #~ import sys
    #~ reload(sys)
    #~ sys.setdefaultencoding("UTF-8")
    import doctest
    doctest.testmod(verbose=True)


if __name__ == "__main__":
    import sys, time, traceback
    print time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        tests()
    except Exception, e:
        if type(e).__name__ == 'COMError':
            print 'COM Error, msg [%s]' % e
        else:
            print 'Error, program failed:'
            traceback.print_exc(file=sys.stderr)
    print time.strftime('%Y-%m-%d %H:%M:%S')
