####
##
##  schema_generator.py
##
##  Generate a Workato-compatible schema definition from an API-generated
##  JSON response.
##
##  USAGE
##      $ python schema_generator.py <response_to_parse> [<output_file>]
##      
##      <response_to_parse>     A .json file containing the API-generated response
##      <output_file>           [optional] specify the name of the output file
##
##  EXAMPLE
##      If you submit a file containing the following:
##
##          {
##              "name": "george",
##              "type": "dog",
##              "age": 3,
##              "home": ["123 Sunflower Rd.", "New York, NY", "1-234-567-8910"],
##              "diet": {"food": "Iams", "treats": "Milkbones", "other": "occassional table scraps"}
##              "lastVisit": "2022-10-01T12:35:10.000-500"
##          }
##
##      ...we would expect to see the following output...
##
##          [
##              { name: "name", type: "string" },
##              { name: "type", type: "type" },
##              { name: "age", type: "integer" },
##              { name: "home", type: "array", of: "string" },
##              { name: "diet", type: "object",
##                paroperties: [
##                  { name: "food", type: "string" },
##                  { name: "treats", type: "string" },
##                  { name: "other", type: "string" }
##                ]
##              },
##              { name: "lastVisit", type: "datetime" }
##          ]
##
####

import json
import sys
from datetime import datetime, date
#from types import NoneType

# set source and output files based on arguments passed
sf = "./data/schemas/{fn}".format(fn=sys.argv[1])
#if sys.argv[2]:
#    of = sys.argv[2]
#else:
of = ".".join(sf.split(".")[:-1]) + ".rb" #"./data/schemas/{fn}".format(fn=".".join(sf.split(".")[:-1]) + ".rb")

# load JSON for parsing
src = open(sf)
model = json.load(src)

dataTypes = {
    str: "string",
    int: "int",
    float: "decimal",
    datetime: "date_time",
    date: "date",
    bool: "boolean",
    dict: "object",
    list: "array",
    None: "void"
}

def parseField(fieldName, fieldValue):
    fieldObject = {}
    if type(fieldValue) != dict and type(fieldValue) != list:
        if fieldValue is not None:
            fieldObject = {"name": fieldName, "type": dataTypes[type(fieldValue)]}
        else:
            fieldObject = {"name": fieldName, "type": "string"}
    elif type(fieldValue) == list:
        if len(fieldValue) > 0:
            if type(fieldValue[0]) != dict:
                dataType = dataTypes[type(fieldValue[0])]
                fieldObject = {"name": fieldName, type: "array", "of": dataType}
            # elif type(fieldValue[0]) == list: # workato doesn't accept nested arrays in schema
            elif type(fieldValue[0]) == dict:
                dataType = "object"
                properties = []
                for ef in fieldValue[0]:
                    subfieldObject = parseField(ef, fieldValue[0][ef])
                    properties.append(subfieldObject)
                fieldObject = {"name": fieldName, "type": "array", "of": dataType, "properties": properties}
        else:
            dataType = "string"
            fieldObject = {"name": fieldName, "type": "array", "of": dataType}
    elif type(fieldValue) == dict:
        dataType = "object"
        properties = []
        for ef in fieldValue:
            subfieldObject = parseField(ef, fieldValue[ef])
            properties.append(subfieldObject)
        fieldObject = {"name": fieldName, "type": dataType, "properties": properties}
    return fieldObject

#def formatOutput(object):
#    formattedString = "{\n"
#    for ef in object:
#        if type(object[ef]) != list:
#            formattedString += "\t%s\: \"%s\"" % (ef, object[ef])
#        else:
#            for eo in object[ef]:
#
#    return formattedString

def main(sourceData, outFile):
    schemaModel = []
    for ef in sourceData:
        fn = ef
        fv = sourceData[ef]
        fieldObj = parseField(fn, fv)
        schemaModel.append(fieldObj)
    with open(outFile, "w") as out:
        for each in schemaModel:
            jsonified = json.dumps(each, indent=4)
            out.write(jsonified)
            out.write(",\n")

main(model, of)