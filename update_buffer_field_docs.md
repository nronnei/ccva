#Update Buffer Field
##Metadata
*Tool Name:*  update_buffer_field.py

*Tool Type:*  standalone script

*Tool Author:*  Nicholas Ronnei (nronnei@gmail.com) 

*Created for use on the Ramsey County Climate Change Vulnerability Assessment*

##Synopsis
This is a short and sweet, standalone script that I used in creating the “Extreme Exposure” layer used in the Air Quality Assessment.  It uses Road Character values from the NCompass Metro Dataset to determine which buffer value the road receives.  This buffer field is later used as an input to the Buffer tool to create the “Extreme Exposure” layer.

##Details
Looking at the script, one can see it relies on the `arcpy` site package and ESRI `.shp` files and/or feature classes.  It uses manually entered field names and values contained in the `fields`, `rc_vals` (for reading), and `buf_vals` (for writing) respectively.  By changing these, one can apply the logic of the script to any other table.  If Row 1 contains Value A in the first specified field, then the script will write Value X in the second specified field.  If it contains Value B, the script writes Value Y.  If it contains Value C, then the script writes Value Z.  If it contains Value D, then the script logs an error and continues through each row in the table.

This all occurs in the table of whatever feature class is reference by the `fc` variable.  Changing the path changes the file referenced.  As such, it is HIGHLY RECCOMMENDED that you run this script on a copy of the file you want to work on, as `fc` will be irreversibly altered.  The reading/writing is accomplished through the use of an Update Cursor from the `.da` module of `arcpy` which allows direct data access for better speed.
See the code directly for helpful comments.
