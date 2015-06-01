## Author: Nick Ronnei (nronnei@gmail.com)
## Written in Python 2.7 for use with ArcGIS

from __future__ import division
import arcpy
import math
import csv
import os
import sys

######
## Define functions necessary for the script
######


def calculate_estimate(inList):
    """
    Sum values from the rows of a table.
    :param inList: 2d "array" containing values from a row in a table to be summed.
    :return: A list containing the sums of the rows from inList.
    """
    outList = []
    for row in inList:
        sum = 0
        for val in row:
            sum += long(val)
        outList.append(sum)
    return outList


def standard_MoE(inList):
    """
    Calculates Margin of Error (MoE) for more than two estimates combined by simple linear addition.
    :param inList: 2d "array" containing values from a row in a table to be summed.
    :return: A list containing the proper MoEs for the new estimates (one value per table row).
    """
    outList = []
    for row in inList:
        seList = []
        if len(row) > 1:
            for moe in row:
                se = moe / 1.645
                sq_se = se * se
                seList.append(sq_se)
            t = 0
            for se in seList:
                t += se
            a = (math.sqrt(t))
            b = a * 1.645
            c = int(round(b))
            outList.append(c)
        else:
            a = row[0]
            outList.append(a)
    return outList


def update_report(inData, outPath):
    with open(outPath, 'ab') as f:
        writer = csv.writer(f)
        for row in inData:
            writer.writerow(row)


def get_mean(inList):
    sum = 0
    den = 0
    for item in inList:
        if item is None:
            pass
        else:
            sum += item
            den += 1
    mean = sum / den
    return mean


def get_median(inList):
    med_list = []
    for item in inList:
        if item is None:
            pass
        else:
            med_list.append(item)
    t = len(med_list)
    med_list.sort()
    if t % 2 == 0:
        i = int(t / 2)
        num = med_list[i - 1] + med_list[i]
        median = num / 2
    else:
        i = int((t / 2) - 0.5)
        median = inList[i]
    return median


######
## Get the inputs, set up the data for processing
######

## Get parameters from the ArcMap Tool UI
in_data = arcpy.GetParameterAsText(0)
in_f = arcpy.GetParameterAsText(1).encode("ascii")
n_field = arcpy.GetParameterAsText(2).encode("ascii")
edit_field = arcpy.GetParameterAsText(3).encode("ascii")
desc = arcpy.GetParameterAsText(4).encode("ascii")
out_data = arcpy.GetParameterAsText(5)
out_report = arcpy.GetParameterAsText(6)

## See if we need to create new fields, or if they already exist.
ef1 = edit_field + "_e1"  # Will be the simple sum of the estimates
ef2 = edit_field + "_m1"  # Will be the MoE of the linear addition of estimates
ef3 = edit_field + "_e2"  # Will be the normalized version of the estimate
ef4 = edit_field + "_m2"  # Will be the MoE for the normalized version of the estimate as a decimal percentage
ef5 = edit_field + "_e3"  # Will be the normalized version times 1,000,000
editList = [ef1, ef2, ef3, ef4, ef5]
startFields = arcpy.ListFields(out_data)
for f in editList:
    if f in startFields:
        arcpy.AddWarning("Field {0} already exists. Recalculating field.".format(f))
    else:
        if f.endswith("e1") or f.endswith("m1"):
            arcpy.AddField_management(out_data, f, "SHORT")
        elif f.endswith("e3"):
            arcpy.AddField_management(out_data, f, "LONG")
        else:
            arcpy.AddField_management(out_data, f, "FLOAT")


## Set up proper in_fields list for estimate values
e_fields = []
in_list = in_f.split(";")
for item in in_list:
    new = item.lstrip(" ")
    e_fields.append(new)


##  Create list of MoE counterparts for E input fields
m_fields = []
for field in e_fields:
    new = field.replace("e", "m")
    m_fields.append(new)

#####
## Calculate the values of "ef1"
#####

estCalcList = []  # Holds all the original estimates for each row so we can use the calculation function

if len(e_fields) == 1:
    f = e_fields[0]
    with arcpy.da.SearchCursor(in_data, f) as sCursor:
        for row in sCursor:
            val = row[0]
            estCalcList.append(val)
else:
    with arcpy.da.SearchCursor(in_data, e_fields) as sCursor:
        for row in sCursor:
            rowList = []
            for x in range(0, len(e_fields)):
                val = row[x]
                rowList.append(val)
            estCalcList.append(rowList)

# Do the math and put the values in a new list
ef1Values = calculate_estimate(estCalcList)  # calculate_estimate returns a list which holds the
                                             # final calculations of aggregate estimates for each row.

# Write the values to the table
with arcpy.da.UpdateCursor(out_data, ef1) as uCursor:
    r = 0  # Row counter (you will see this throughout, it means the same thing).
    for row in uCursor:
        row[0] = ef1Values[r]
        uCursor.updateRow(row)
        r += 1

#####
## Calculate the values of "ef2"
#####

ef2Values = []  # Holds the final calculations of MoE for each row
mCalcList = []  # Holds all the original MoE values for each row so we can use the calculation function

# Calculate MoE for just 1 field entry
if len(m_fields) == 1:
    f = m_fields[0]
    with arcpy.da.SearchCursor(in_data, f) as sCursor:
        for row in sCursor:
            val = row[0]
            ef2Values.append(val)  # Append the value to the final values list

# Calculate MoE for 2 or more field entries
else:
    compareList = []
    for f in e_fields:
        compareList.append(f)
    for f in m_fields:
        compareList.append(f)
    compareList.sort()
    with arcpy.da.SearchCursor(in_data, compareList) as sCursor:
        for row in sCursor:
            rowList = []
            zeroFlag = False  # Checks if we have already added 1 zero estimate or not
            for x in range(0, len(m_fields)):
                adjust = len(m_fields)
                mVal = row[adjust + x]  # MoE value of the given row
                eVal = row[x]  # Estimate value of the given row
                if eVal == 0:
                    if zeroFlag:
                        pass
                    else:
                        rowList.append(mVal)
                        zeroFlag = True
                else:
                    rowList.append(mVal)
            mCalcList.append(rowList)

    ef2Values = standard_MoE(mCalcList)  # standard_MoE returns a list which holds the
                                         # final calculations of aggregate MoEs for each row.

# Write values to the table
with arcpy.da.UpdateCursor(out_data, ef2) as uCursor:
    r = 0
    for row in uCursor:
        row[0] = ef2Values[r]
        uCursor.updateRow(row)
        r += 1

#####
## Calculate the values of "ef3"
#####

ef3Values = []
with arcpy.da.SearchCursor(in_data, n_field) as sCursor:
    r = 0
    for row in sCursor:
        den = row[0]  # Value of normalize field
        num = ef1Values[r]  # Value of ef1
        nVal = None
        if den != 0:
            nVal = float(num / den)
        else:
            pass
        ef3Values.append(nVal)
        r += 1

# Write values to table
with arcpy.da.UpdateCursor(out_data, ef3) as uCursor:
    c = 0  # Row counter (you will see this throughout, it means the same thing).
    for row in uCursor:
        row[0] = ef3Values[c]
        uCursor.updateRow(row)
        c += 1

#####
## Calculate the values of "ef4"
#####

ef4Values = []
nMoE = n_field.replace("e", "m")
ef4Fields = [n_field, nMoE]
with arcpy.da.SearchCursor(in_data, ef4Fields) as sCursor:
    r = 0
    for row in sCursor:
        chk = [row[0], row[1], ef3Values[r]]
        nullFlag = False
        for val in chk:
            if val is None:
                nullFlag = True
                break
            else:
                pass
        if nullFlag:
            ef4Values.append(None)
        else:
            try:
                standardMoE = ef2Values[r] ** 2  # Value of new estimate's MoE
                proportion = ef3Values[r] ** 2  # Value of normalized estimate
                normalizeField = row[0]  # Value of the normalize field's estimate
                normalizeMoE = row[1] ** 2  # Normalize field's MoE

                a = proportion * normalizeMoE
                b = standardMoE - a
                top = math.sqrt(b)
                bot = normalizeField
                if bot != 0:
                    GOLD = float(top / bot)
                else:
                    GOLD = None
                ef4Values.append(GOLD)
            except ValueError:
                ef4Values.append(-99999)
                arcpy.AddError("Woah, you've got some funky numbers there!\n"
                               "You can't take the sqrt of a negative number,\n"
                               "and it seems that the values in row {0} are \n"
                               "causing you some problems. We are working on\n"
                               "improving the tool to handle this problem.".format(str(r)))
                arcpy.AddMessage("RAW VALUE REPORT:\n"
                                 "STANDARD MOE (New Est.) = " + str(ef2Values[r]) + "\n"
                                 "PROPORTION = " + str(ef3Values[r]) + "\n"
                                 "NORMALIZE VALUE = " + str(row[0]) + "\n"
                                 "NORMALIZE MOE = " + str(row[1]) + "\n")
        r += 1

# Write values to table
with arcpy.da.UpdateCursor(out_data, ef4) as uCursor:
    c = 0
    for row in uCursor:
        row[0] = ef4Values[c]
        uCursor.updateRow(row)
        c += 1

#####
## Calculate the values of "ef5"
#####

ef5Values = []
for val in ef3Values:
    if val is not None:
        e = long(val * 1000000)
    else:
        e = val
    ef5Values.append(e)

# Write values to table
with arcpy.da.UpdateCursor(out_data, ef5) as uCursor:
    c = 0
    for row in uCursor:
        row[0] = ef5Values[c]
        uCursor.updateRow(row)
        c += 1
del uCursor
del sCursor

#####
## Add new variable to the VarReport
#####

newVarReport = []  # Will hold each line of the report for writing to CSV
if out_report == '':
    cwd = os.getcwd()
    (t_dir, s_dir) = os.path.split(cwd)
    np = t_dir + "\\Reports\\CreatedVariables.csv"
    out_report = np
else:
    pass

## ef1Values Report
code = ef1
name = "Number of " + desc
used_vars = str(e_fields)
mean = get_mean(ef1Values)
median = get_median(ef1Values)
notes = ''
ef1Rep = [code, name, used_vars, mean, median, notes]
newVarReport.append(ef1Rep)

## ef2Values Report
code = ef2
name = "Margin of Error for " + ef1
used_vars = str(m_fields)
mean = get_mean(ef2Values)
median = get_median(ef2Values)
notes = ''
ef2Rep = [code, name, used_vars, mean, median, notes]
newVarReport.append(ef2Rep)

## ef3Values Report
code = ef3
name1 = "Percent of " + desc
used_vars = str([ef1, n_field])
mean = get_mean(ef3Values)
median = get_median(ef3Values)
notes = ''
ef3Rep = [code, name1, used_vars, mean, median, notes]
newVarReport.append(ef3Rep)

## ef4Values Report
code = ef4
name = "Margin of Error for " + ef3
used_vars = str([ef2, ef3, n_field, nMoE])
notes = ''
mean = get_mean(ef4Values)
median = get_median(ef4Values)
ef4Rep = [code, name, used_vars, mean, median, notes]
newVarReport.append(ef4Rep)

## ef5Values Report
code = ef5
name = ef3 + " * 1,000,000"
used_vars = ef3
mean = get_mean(ef5Values)
median = get_median(ef5Values)
notes = 'Only used for creating rasters.  This is the same value as {0}, but must be used for' \
        'raster creation, as Raster Calculator does not like the "Float" type. 1,000,000 was ' \
        'chosen as a multiplier because it stores the first 6 digits of the float in integer form.'
ef5Rep = [code, name, used_vars, mean, median, notes]
newVarReport.append(ef5Rep)

## Write Update
# Create spacer to separate variables
newVarReport.append(["XXXXXXXXXXXXXXX"])
update_report(newVarReport, out_report)
arcpy.AddMessage("Success! Variable {0} was added to the report. You can view the report here: {1}".format(edit_field, out_report))
