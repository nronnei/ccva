#Advanced M.O.E. Tracker
##Metadata
*Tool Name:*  advanced_MOE_tracker.py

*Tool Type:* ArcGIS Toolbox script

*Tool Author:*  Nicholas Ronnei (nronnei@gmail.com) 

*Created for use on the Ramsey County Climate Change Vulnerability Assessment*

##Synopsis
This script was created to help with the annoying problem of Margin of Error tracking when manipulating data from the U.S. Census Bureau's American Communities Survey (ACS).  Under guidance from U.S. Census Bureau documentation and epidemiologists at Ramsey County, I developed this script to deal with combining large numbers of variables which have an estimated value of zero.  Adding a lot of zeros causes problems with margins of error on the ACS.  This tool solves that problem.

This tool also aids in the workflow I used while conducting the Climate Change Vulnerability Assessment (CCVA) at Ramsey County.  After selecting the data you want to combine, it does all the math and creates 5 new fields in a feature of your choice if you select the normalized option (2 if you don't) – one for each new value from the resulting math.  It also creates two new raster files if you use the normalized option, one new raster if you don't.  These new rasters are then open for manipulation in ArcGIS Model Builder.  The second raster is created so that the user can work with integers rather than floats, and contains exactly the same values as the first raster except they are multiplied by 1,000,000 and made integers.

##Details
####Custom Functions
This script uses several custom functions, so I'll walk through them quickly before we begin.  The **first**, “calculate_estimate”, accepts a list of lists (the Python equivalent of a JavaScript 2D array).  It sums all the items in each list and adds them to returned holder list called “outList”. The docstring explains concisely.

The **second function** “standard_MoE” calculates the new margin of error for values added by linear addition in the manner prescribed by the ACS Guidelines.  As before, it accepts a list of list as an input.  All the numbers in each list are converted to standard error and then manipulated.  I chose to round the numbers for the sake of simplicity.  The my goal in tracking Margin of Error was to determine the statistical significance.  Nearly all selected indicators have very, very high margins of error, but several were excluded because their errors were exorbitant. 

The following three functions are used for automated report creation.  The first of the three writes Python lists to a CSV file.  This CSV writer *appends* to the current document, so if you want to create a new CSV and write a header row, great.  It also means that any data you add incrementally will not affect pre-existing data.  The second calculates the mean margin of error for each indicator created by the tool, and the third calculates the median for each.

####Inputs
There are seven user inputs to the tool.  The “in_data” variable refers to the input feature class.  This contains all the Census data that you would like to extract a subset from. The “in_f” variable represents a list fields you'd like to combine.  The user selects them using checkboxes from the tools GUI. Next, “n_field” represents the normalizing field which the user selects from a dropdown menu. 

The next few variables are all about outputs.  The “edit_field” variable accepts a base name for the new fields.  This name can be whatever the user chooses, but I used short code names representing the source data and a number (ex. BG_01 for the first variable I generated from block groups).  The script adds additional codes the the field names in the block beginning with the comment “## See if we need...” depending on what the field will hold.  See inline comments for details.

The “desc” variable holds a short string that explains what the new indicator means.  This is especially useful when using code names for “edit_field” because “desc” is best thought of as a long name.  The script automatically inserts “Number of “ and “Percent of “ at the front of whatever string you enter in “desc” so that you only have to use one description to cover all your bases.  Plan for this when entering “desc”.

Finally, “out_data” and “out_report” are paths to the output feature class and output CSV respectively.  The feature class specified in “out_data” should already exist.  The tool will create new fields for the data you've selected from your master feature class.  This method allows you to separate the data you need to examine from the bulk data provided by the ACS.  The path given in “out_report” leads to the CSV that the tool writes its report in.  It has a default path, but its very buggy and hard to find so I highly recommend providing your own.

####Preprocessing the Data
The first part of the tool sets up all the new field names and checks if they exist.  If they do not exist, the tool creates them.  If they do exist, they will be overwritten. This prevents the script from adding a bunch of extra, unnecessary fields if a variable needs to be recreated.

The next phase (staring with the comment “## Set up proper in_fields...”) converts the user input from the tool into a Python list called “e_fields” because it holds the values from ASC estimate field names selected by the user.  The next loop does the same, but it creates a list called “m_fields” to hold the ASC margin of error field names.

####Calculating “ef1”
First, the script checks how many fields the user selected to combine.  Sometimes this tool is the quickest way to get just one field from the ACS bulk data into a new feature class, so I prepared it for that.  If there is only 1 field in the list, it just fills the holder list with the same values as are in the column.  If there are more than one field selected, it creates a list of the values which it then appends to the holder list (called “estCalcList” in this instance). 

The actual calculation of the estimate values uses the “calculate_estimate” function discussed in **Custom Functions**.  The list of values that the function returns then passes to an update cursor which writes the values to the first new field. 
