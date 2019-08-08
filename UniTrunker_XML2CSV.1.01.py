#!Python

## Written for Python 3 on Windows by Chris VanderSchaaf
## A script to extract the TalkGroups and Radio IDs from Unitrunker XML
## and write a CSV file for each. The RID file is formatted to enable copy
## and paste into UBCD Sentinel
##
## 20190803 - v 1.00 - Initial version
## 20190806 - v 1.01 - Added 'Hit' counts to exports.


from xml.etree import ElementTree
import csv

# Set location of your UniTrunker XML file here in the next line:

xmlSourceFile = 'C:\\Data\\Scanner\\UniTrunker Stuff\\Unitrunker.xml'

tree = ElementTree.parse(xmlSourceFile)
branches = tree.getroot()

### open two output files - 1 for Talkgroups and the other for Radio IDs
# Customise names and folder locations as desired

TalkGroupCSV = 'output_TalkGroups.csv'
RadioIdCSV = 'output_RadioIds.csv'

ofileTG = open(TalkGroupCSV, 'w', newline='')
ofileRID = open(RadioIdCSV, 'w', newline='')

### create a csv writer objects

TGwriter = csv.writer(ofileTG)
RIDwriter = csv.writer(ofileRID)

# Counters so we can add header rows

TgCount = 0
RidCount = 0

rowTgHead = []
rowRidHead = []

for branch in branches: 
    for twig in branch:

        if twig.tag == 'Group':     # Find the TalkGroups records
            tgid = twig.get('id')
            tgUser = twig.get('tag')
            tgName = twig.get('label')
            tgLast = twig.get('last')
            tgLast = tgLast[7:8] + '/' + tgLast[5:6] + '/' + tgLast[0:4]
            tgNotes = twig.get('notes')
            tgHits = twig.get('hits')
            
            if tgUser == None:
                tgUser = ''

            if tgNotes == None:
                tgNotes = ''

            if tgHits == None:
                tgHits = ''
                

            if tgUser != None:  # Filter out TGs with no data and output remainder. 

                
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
                    TgCount = TgCount +1
            
                rowTgData.append(tgid)      # TalkGroup ID
                rowTgData.append(tgUser)    # User - RFS, FRNSW etc
                rowTgData.append(tgName)    # TalkGroup Name
                rowTgData.append(tgLast)    # Date last seen by UniTrunker
                rowTgData.append(tgNotes)   # Comments
                rowTgData.append(tgHits)    # Hits
                
                # Write record to CSV
                TGwriter.writerow(rowTgData)
           
        if twig.tag == 'User':      # Find the Radio ID records
            radioId = twig.get('id')
            radioUser = twig.get('label')
            radioTag = twig.get('tag')
            radioLast = twig.get('last')
            radioLast = radioLast[7:8] + '/' + radioLast[5:6] + '/' + radioLast[0:4]
            radioNotes = twig.get('notes')
            radioHits = twig.get('hits')

            if radioTag == None:
                radioTag = ''

            if radioNotes == None:
                radioNotes = ''

            if radioHits == None:
                radioHits = ''
                
            if radioUser != None: # Filter out RIDs with no data and output remainder. 

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
                    RidCount = RidCount +1
                    
                # Ordered so that I can copy and paste the first four
                # columns into UBCD Sentinel
                
                rowRidData.append(radioUser)    # Callsign
                rowRidData.append(radioId)      # Radio ID
                rowRidData.append('Off')
                rowRidData.append('Off')
                rowRidData.append(radioTag)     # Tag - Short note
                rowRidData.append(radioLast)    # Date last seen by UniTrunker
                rowRidData.append(radioNotes)   # Comments
                rowRidData.append(radioHits)    # Hits
                
                # Write record to CSV 
                RIDwriter.writerow(rowRidData)

ofileRID.close()
ofileTG.close()


