# UniTrunker-XML2CSV
Python script to extract TalkGroups and Radio IDs from UniTrunker XML files and write to CSV

V1.065 - Changes:
* Added exporting the converted file to DSD Group Aliases and to SDR Trunk playlist XML format for pasting into the respective files. Always make a backup copy of the files before editing. 
* The Group Tag and User Tag variables now reference 'brief' field instead of 'tag' field as tag was repurposed within Unitrunker.

V1.05 - Changes:
* Added a switch to control creation of generic Radio IDs or exclusion for unknown radios. 

V1.04 - Changes:
* Bug fix - Conversion of timestamps to dates corrected.
* Code cleanup

V1.03 - Changes: 
* Filter out Radio IDs of known encrypted users
* Generate generic radio user tag of service description + last 3-5 digits of RID where no RID tag is recorded. Applies to main non-encrypted NSW GRN user groups only. Others that are left blank will be filtered out.
