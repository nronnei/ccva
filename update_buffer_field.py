## Author: Nick Ronnei (nronnei@gmail.com)

import arcpy, sys

def FieldExists(featureclass, fieldname):
    fieldList = arcpy.ListFields(featureclass, fieldname)

    fieldCount = len(fieldList)

    if (fieldCount == 1):
        return True
    else:
        return False


## Declare variables
fc = r"C:\GIS\CCVA\Risk.gdb\AQ_MajorRoadsRC"
fields = ['RD_CHAR', 'BUFFER']
rc_vals = ['RC10', 'RC20', 'RC30']
buf_vals = ['1600 Feet', '1300 Feet', '1000 Feet']

## Verify that the specified table extists (Verify Table Name = vtn)
vtn = arcpy.Exists(fc)
if vtn:
    print "FC validated... \n"
else:
    print "Failed to locate the table, check the path."
    sys.exit()

## Verify that the specified table extists (Verify Field Name = vfn)
## If it does not exist, add the field
vfn = FieldExists(fc, fields[1])
if vfn:
    print "Field already exists...\n"
else:
    arcpy.AddField_management(fc, buf, 'Text')
    print "Field created! \n"

## Update the 'BUFFER' field with a value depending on 
## the value of 'RD_CHAR'
rowCount = 0
with arcpy.da.UpdateCursor(fc, fields) as cursor:
    for row in cursor:
        if row[0] == rc_vals[0]:
            row[1] = buf_vals[0]
        elif row[0] == rc_vals[1]:
            row[1] = buf_vals[1]
        elif row[0] == rc_vals[2]:
            row[1] = buf_vals[2]
        else:
            "Something has gone horribly wrong! the value of RD_CHAR is {0}".format(row[0])
        rowCount += 1
        cursor.updateRow(row)
        if rowCount % 100 == 0:
            print str(rowCount) + ' rows counted...'

print "\n\n\nAll done!"
