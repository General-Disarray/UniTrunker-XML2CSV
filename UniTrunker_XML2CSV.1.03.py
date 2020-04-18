#!Python

# Written for Python 3 on Windows by Chris VanderSchaaf
# A script to extract the TalkGroups and Radio IDs from Unitrunker XML
# and write a CSV file for each. The RID file is formatted to enable copy
# and paste into UBCD Sentinel
#
# 20190803 - v 1.00 - Initial version
# 20190806 - v 1.01 - Added 'Hit' counts to exports.
# 20190416 - v 1.03 - Added generic radio ID tag creation and exclusions for known encrypted users

from xml.etree import ElementTree
import csv


def include_rid(rid):

    # test radioId number range to include in export list
    # include = false for blank and encrypted users -
    # construct a dictionary of the radio ID ranges
    # if radioId in exclusions dictionary then return exportRid = false

    exclusions = {
        1: {"rangeStart": 210000, "rangeEnd": 799999, "label": "encrypted user"},
        2: {"rangeStart": 2100000, "rangeEnd": 2100999, "label": "encrypted user"},
        3: {"rangeStart": 2110000, "rangeEnd": 2119999, "label": "encrypted user"},
        4: {"rangeStart": 2120000, "rangeEnd": 2129999, "label": "encrypted user"},
        5: {"rangeStart": 2175000, "rangeEnd": 2175999, "label": "encrypted user"},
        6: {"rangeStart": 2600000, "rangeEnd": 2600099, "label": "encrypted user"},
        7: {"rangeStart": 2659000, "rangeEnd": 2659499, "label": "encrypted user"},
        8: {"rangeStart": 2659500, "rangeEnd": 2659599, "label": "encrypted user"},
        9: {"rangeStart": 2661000, "rangeEnd": 2661999, "label": "encrypted user"}
    }

    for row, info in exclusions.items():
        if int(info["rangeStart"]) <= int(rid) <= int(info["rangeEnd"]):
            print("Not writing record for " + rid + "-" + info["label"])
            exportRid = 'no'

            return exportRid


def check_label(rid):

    # We can also populate some blanks with basic data:
    # If no radioID, create a generic service based tag
    # using the last 'labelDigits' numbers of the RID

    genericRids = {
        1: {"rangeStart": 2000000, "rangeEnd": 2009999, "label": "FRNSW", "labelDigits": 5},
        2: {"rangeStart": 2010000, "rangeEnd": 2039999, "label": "RFS", "labelDigits": 5},
        3: {"rangeStart": 2044000, "rangeEnd": 2069999, "label": "SES", "labelDigits": 5},
        4: {"rangeStart": 2070000, "rangeEnd": 2079999, "label": "FRNSW", "labelDigits": 5},
        5: {"rangeStart": 2130000, "rangeEnd": 2130099, "label": "YTH JSTCE", "labelDigits": 3},
        6: {"rangeStart": 2220000, "rangeEnd": 2221999, "label": "AUSGRID", "labelDigits": 4},
        7: {"rangeStart": 2230000, "rangeEnd": 2230999, "label": "INTEGRAL", "labelDigits": 3},
        8: {"rangeStart": 2240000, "rangeEnd": 2240199, "label": "HTR WTR", "labelDigits": 3},
        9: {"rangeStart": 2300000, "rangeEnd": 2300599, "label": "ARTC", "labelDigits": 3},
        10: {"rangeStart": 2310000, "rangeEnd": 2331999, "label": "AMBO", "labelDigits": 5},
        11: {"rangeStart": 2350000, "rangeEnd": 2350999, "label": "SYD FERRY", "labelDigits": 3},
        12: {"rangeStart": 2370000, "rangeEnd": 2379999, "label": "RAILCORP", "labelDigits": 4},
        13: {"rangeStart": 2380000, "rangeEnd": 2380999, "label": "RMS.Roads", "labelDigits": 4},
        14: {"rangeStart": 2390000, "rangeEnd": 2390099, "label": "HATZOLAH", "labelDigits": 3},
        15: {"rangeStart": 2420000, "rangeEnd": 2420999, "label": "OEH.Parks", "labelDigits": 3},
        16: {"rangeStart": 2430000, "rangeEnd": 2439999, "label": "RMS.Maritime", "labelDigits": 4},
        17: {"rangeStart": 2448000, "rangeEnd": 2448999, "label": "Fisheries", "labelDigits": 3},
        18: {"rangeStart": 2450000, "rangeEnd": 2459999, "label": "WaterNSW", "labelDigits": 4},
        19: {"rangeStart": 2480000, "rangeEnd": 2480999, "label": "OEH.Forestry", "labelDigits": 3},
    }

    s_radioId = str(rid)
    for row, info in genericRids.items():
        if int(info["rangeStart"]) <= int(rid) <= int(info["rangeEnd"]):
            # Determine the number of digits to retrieve - varies from service to service
            startDigit = len(rid) - int(info["labelDigits"])
            radioUser = info["label"] + "." + s_radioId[startDigit:7]
            print("Writing record for " + s_radioId + " - " + radioUser)

            return radioUser


def main():

    # Set location of your UniTrunker XML file here in the next line:

    xmlSourceFile = 'D:\\Data\\Scanner\\UniTrunker Stuff\\Unitrunker.xml'

    tree = ElementTree.parse(xmlSourceFile)
    branches = tree.getroot()

    # Open two output files - 1 for Talkgroups and the other for Radio IDs
    # Customise names and folder locations as desired

    TalkGroupCSV = 'output_TalkGroups.csv'
    RadioIdCSV = 'output_RadioIds.csv'

    ofileTG = open(TalkGroupCSV, 'w', newline='')
    ofileRID = open(RadioIdCSV, 'w', newline='')

    # create csv writer objects

    TGwriter = csv.writer(ofileTG)
    RIDwriter = csv.writer(ofileRID)

    # Counters

    TgCount = 0
    RidCount = 0
    RowCounter = 0

    rowTgHead = []
    rowRidHead = []

    for branch in branches:
        for twig in branch:
            if twig.tag == 'Group':  # Find the TalkGroups records
                tgid = twig.get('id')
                tgUser = twig.get('tag')
                tgName = twig.get('label')
                tgLast = twig.get('last')
                tgLast = tgLast[7:8] + '/' + tgLast[5:6] + '/' + tgLast[0:4]
                tgNotes = twig.get('notes')
                tgHits = twig.get('hits')

                if tgUser is None:
                    tgUser = ''

                if tgNotes is None:
                    tgNotes = ''

                if tgHits is None:
                    tgHits = ''

                if tgUser is not None:  # Filter out TGs with no data and output remainder.

                    rowTgData = []

                    # Create Column Headers. Don't forget to change
                    # these if you change field order.

                    if TgCount == 0:
                        rowTgHead.append('TGID')
                        rowTgHead.append('TG_User')
                        rowTgHead.append('TG_Name')
                        rowTgHead.append('Last Heard')
                        rowTgHead.append('Notes')
                        rowTgHead.append('Hits')

                        TGwriter.writerow(rowTgHead)
                        TgCount = TgCount + 1

                    rowTgData.append(tgid)  # TalkGroup ID
                    rowTgData.append(tgUser)  # User - RFS, FRNSW etc
                    rowTgData.append(tgName)  # TalkGroup Name
                    rowTgData.append(tgLast)  # Date last seen by UniTrunker
                    rowTgData.append(tgNotes)  # Comments
                    rowTgData.append(tgHits)  # Hits

                    # Write record to CSV
                    TGwriter.writerow(rowTgData)

            if twig.tag == 'User':  # Find the Radio ID records
                radioId = twig.get('id')
                radioUser = twig.get('label')
                radioTag = twig.get('tag')
                radioLast = twig.get('last')
                radioLast = radioLast[7:8] + '/' + radioLast[5:6] + '/' + radioLast[0:4]
                radioNotes = twig.get('notes')
                radioHits = twig.get('hits')

                if radioTag is None:
                    radioTag = ''

                if radioNotes is None:
                    radioNotes = ''

                if radioHits is None:
                    radioHits = ''

                # if radioUser is None: # See if we can assign a generic label
                if radioUser is None:
                    radioUser = check_label(radioId)

                if radioUser is not None:  # Filter out RIDs with no data and output remainder.
                    rowRidData = []

                    # Create Column Headers. Don't forget to change
                    # these if you change field order.

                    if RidCount == 0:
                        rowRidHead.append('Callsign')
                        rowRidHead.append('RadioID')
                        rowRidHead.append('Alert Tone')
                        rowRidHead.append('Alert Light')
                        rowRidHead.append('Tag')
                        rowRidHead.append('Last Heard')
                        rowRidHead.append('Notes')
                        rowRidHead.append('Hits')
                        RIDwriter.writerow(rowRidHead)
                        RidCount = RidCount + 1

                        # Ordered so that I can copy and paste the first four
                        # columns into UBCD Sentinel

                        # Call function to test Radio ID.
                        # If it's a known encrypted user, discard

                    if include_rid(radioId) != 'no':
                        rowRidData.append(radioUser)  # Callsign
                        rowRidData.append(radioId)  # Radio ID
                        rowRidData.append('Off')
                        rowRidData.append('Off')
                        rowRidData.append(radioTag)  # Tag - Short note
                        rowRidData.append(radioLast)  # Date last seen by UniTrunker
                        rowRidData.append(radioNotes)  # Comments
                        rowRidData.append(radioHits)  # Hits

                        # Write record to CSV
                        RowCounter = RowCounter + 1
                        RIDwriter.writerow(rowRidData)
    ofileRID.close()
    ofileTG.close()
    print("\nWrote " + str(RowCounter) + " records")

main()


