# UniTrunker-XML2CSV
Python script to extract TalkGroups and Radio IDs from UniTrunker XML files and write to CSV

V1.04 - Changes:
Bug fix - Conversion of timestamps to dates corrected.
Code cleanup

V1.03 - Changes: 
* Filter out Radio IDs of known encrypted users
* Generate generic radio user tag of service description + last 3-5 digits of RID where no RID tag is recorded. Applies to main non-encrypted NSW GRN user groups only. Others that are left blank will be filtered out.
