#!Python

# Written for Python 3 on Windows by Chris VanderSchaaf
# Designed for working with the New South Wales Govt Radio Network.
# A script to extract the TalkGroups and Radio IDs from Unitrunker XML
# and write a CSV file for each. The RID file is formatted to enable copy
# and paste into UBCD Sentinel
#
# 20190803 - v 1.00 - Initial version
# 20190806 - v 1.01 - Added 'Hit' counts to exports.
# 20200416 - v 1.03 - Added generic radio ID tag creation and exclusions for known encrypted users
# 20200509 - v 1.04 - Bug fix - Conversion of timestamp to date corrected.; Optimisations
# 20200520 - v 1.06 - Change default for Generic RID creation to 'no'.
#                     Added to encrypted exclusions
#                     Radio user tags now converted to upper case
# 20200816 - v 1.062 - Added routine to export TG alias info for DSD+ Fastlane and SDR Trunk.
#                     Copy and paste the output into Playlist.xml for SDR Trunk.
# 20211110 - v 1.064 - Remove some invalid RIDs in the zero to 1000 range


from xml.etree import ElementTree
from datetime import datetime
import csv
import re

#def select_ouptuts():

#    output_DsdPlus = 'true'
#    output_SdrTrunk = 'true'
#    output_Sentinel = 'true'

    


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
        9: {"rangeStart": 2661000, "rangeEnd": 2661999, "label": "encrypted user"},
        10: {"rangeStart": 9020000, "rangeEnd": 9025000, "label": "encrypted user"},
        11: {"rangeStart": 9253000, "rangeEnd": 9256999, "label": "encrypted user"},
        12: {"rangeStart": 0, "rangeEnd": 9999, "label": "noise"}
    }

    for row, info in exclusions.items():
        if int(info["rangeStart"]) <= int(rid) <= int(info["rangeEnd"]):
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
        15: {"rangeStart": 2420000, "rangeEnd": 2420999, "label": "DPIE.Parks", "labelDigits": 3},
        16: {"rangeStart": 2430000, "rangeEnd": 2439999, "label": "RMS.Maritime", "labelDigits": 4},
        17: {"rangeStart": 2448000, "rangeEnd": 2448999, "label": "Fisheries", "labelDigits": 3},
        18: {"rangeStart": 2450000, "rangeEnd": 2459999, "label": "WaterNSW", "labelDigits": 4},
        19: {"rangeStart": 2480000, "rangeEnd": 2480999, "label": "DPIE.Forestry", "labelDigits": 3},
    }

    s_radioId = str(rid)
    for row, info in genericRids.items():
        if int(info["rangeStart"]) <= int(rid) <= int(info["rangeEnd"]):
            # Determine the number of digits to retrieve - varies from service to service
            startDigit = len(rid) - int(info["labelDigits"])
            radioUser = info["label"] + "." + s_radioId[startDigit:7]

            return radioUser


def clean(field):
    if field is None:
        field = ''
        return field
    else:
        return field


def uCase(field):
    if field is not None:
        field = field.upper()
    return field


def get_last(seen):
    if seen is not None:
        slicetime = seen[6:8] + '/' + seen[4:6] + '/' + seen[:4]
        return slicetime


def get_last_dsd(seen):
    # in format last="20200917180302"
    # out format last="2020/09/17 18:03"
    if seen is not None:
        dsdtime = seen[:4] + '/' + seen[4:6] + '/' + seen[6:8] + ' ' + seen[8:10] + ':' + seen[10:12]
        return dsdtime


def formatFrequency(frequency):
    if frequency.isnumeric():
        frequency = frequency / 1000000
        return frequency


def writeSdrTgAliasRow(outfile, talkgroup, alias):
    protocol = 'APCO25'
    color = '0'
    listname = 'NSWGRN'
    idtype = 'talkgroup'
    alias = clean(alias)

    if isinstance(alias, str):
        alias = alias.strip()
        alias = re.sub('[&]', '.', alias)

    talkgroup = clean(talkgroup)
    talkgroup = str(talkgroup)

    outfile.write('  <alias name=\"' + alias
                  + '\" color=\"' + color
                  + '\" group=\"' + talkgroup
                  + '\" list=\"' + listname
                  + '\">\n    <id type=\"' + idtype
                  + '\" value=\"' + talkgroup
                  + '\" protocol=\"' + protocol
                  + '\"/>\n  </alias>\n')


def writeSdrRadioAliasRow(outfile, radioId, alias):
    protocol = 'APCO25'
    color = '0'
    listname = 'NSWGRN'
    idtype = 'radio'
    alias = clean(alias)

    if isinstance(alias, str):
        alias = alias.strip()
        alias = re.sub('[&]', '.', alias)

    radioId = clean(radioId)
    radioId = str(radioId)

    outfile.write('  <alias name=\"' + alias
                  + '\" color=\"' + color
                  + '\" list=\"' + listname
                  + '\">\n    <id type=\"' + idtype
                  + '\" value=\"' + radioId
                  + '\" protocol=\"' + protocol
                  + '\"/>\n  </alias>\n')


def writeDSDTgAliasRow(outfile, talkgroup, lastseen, user, alias):

    # line format: protocol, networkID, group, priority, override, hits, timestamp, "group alias"

    dsdProtocol = 'P25'
    dsdNetworkId = 'BEE00.2D1'
    dsdPriority = '50'
    dsdOverride = 'Normal'
    dsdHits = '0'
    dsdTimeStamp = str(lastseen)
    alias = clean(alias)

    if isinstance(alias, str):
        alias = alias.strip()
        alias = re.sub('[&]', '.', alias)

    alias = user + '.' + alias
    talkgroup = clean(talkgroup)
    talkgroup = str(talkgroup)

    outfile.write(dsdProtocol
                  + ',    ' + dsdNetworkId
                  + ',    ' + talkgroup
                  + ',    ' + dsdPriority
                  + ',    ' + dsdOverride
                  + ',    ' + dsdHits
                  + ',    ' + dsdTimeStamp
                  + ',    \"' + alias + '\"\n')


def hex2dec(hexstring):
    try:
        decimalvalue = int(hexstring, 16)
        return decimalvalue
    except:
        decimalvalue = ''
        return decimalvalue

def main():

    # Set location of your UniTrunker XML file here in the next line:

    xmlSourceFile = 'Unitrunker.xml'

    tree = ElementTree.parse(xmlSourceFile)
    branches = tree.getroot()

    # Open a pair of output files - 1 for Talkgroups and the other for Radio IDs
    # Customise names and folder locations as desired

    # Create generic radio ids?
    # Set this to 'no' if you want to keep displaying raw RadioIDs
    # on your scanner.
    createGenericRids = 'no'

    datestamp = datetime.today().strftime('%Y%m%d')

    # Output file names & locations:
    TalkGroupCSV = 'output_TalkGroups_' + datestamp + '.csv'
    RadioIdCSV = 'output_RadioIds.csv_' + datestamp + '.csv'

    # This output file is formatted for pasting TalkGroups into SDR Trunk Playlists
    sdrAliasInsert = 'playlist_Aliases_' + datestamp + '.txt'

    # This output file is formatted for pasting TalkGroups into DSD.Groups alias list
    dsdTgAlias = 'dsd.alias.groups_' + datestamp + '.txt'

    ofileTG = open(TalkGroupCSV, 'w', newline='')
    ofileRID = open(RadioIdCSV, 'w', newline='')
    ofSDR = open(sdrAliasInsert, 'w', newline='')
    ofDsdGroups = open(dsdTgAlias, 'w', newline='')

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
#                tgUser = clean(twig.get('tag'))
                tgUser = clean(twig.get('brief'))
                tgName = clean(twig.get('label'))
                tgLast = get_last(twig.get('last'))
                tgDsdLast = get_last_dsd(twig.get('last'))
                tgNotes = clean(twig.get('notes'))
                tgHits = clean(twig.get('hits'))

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

                    # Write Talkgroup to the SDRTrunk Alias stage file
                    writeSdrTgAliasRow(ofSDR, tgid, tgName)

                    # Write Talkgroup to the DSD Plus Alias stage file
                    writeDSDTgAliasRow(ofDsdGroups, tgid, tgDsdLast, tgUser, tgName)

            if twig.tag == 'User':  # Find the Radio ID records
                radioId = twig.get('id')
                radioUser = (twig.get('label'))
                #radioTag = clean(twig.get('tag'))
                radioTag = clean(twig.get('brief'))
                radioLast = get_last(twig.get('last'))
                radioNotes = clean(twig.get('notes'))
                radioHits = clean(twig.get('hits'))

                # if radioUser is None see if we can assign a generic label
                if radioUser is None:
                    if createGenericRids == 'yes':
                        radioUser = check_label(radioId)

                if radioUser is not None:  # Filter out RIDs with no data and output remainder.
                    radioUser = uCase(radioUser)  # Comment this line out if you don't want forced upper case RID labels
                    rowRidData = []

                    # Create Column Headers. Don't forget to change
                    # these if you change field order.

                    if RidCount == 0:
                        rowRidHead.append('Callsign')
                        rowRidHead.append('RadioID')
                        rowRidHead.append('Alert Tone')
                        rowRidHead.append('Alert Light')
                        #rowRidHead.append('Tag')
                        rowRidHead.append('Brief')
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
                        # Write Talkgroup to the SDRTrunk Alias stage file
                        writeSdrRadioAliasRow(ofSDR, radioId, radioUser)

    ofileRID.close()
    ofileTG.close()
    print("\nWrote " + str(RowCounter) + " records")


main()


