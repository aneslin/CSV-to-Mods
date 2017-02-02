import xml.etree.ElementTree as etree 
import os
import csv
from sys import argv




def idFinder(fileName):
    #find the identifier in a mods file
    tree=etree.parse(fileName)
    root=tree.getroot()
    for node in root.iter('{http://www.loc.gov/mods/v3}mods'):
        x=node.find('{http://www.loc.gov/mods/v3}identifier').text
        return x
def addData(parent,field,txt):
    #add a new subfield,with text 
    c=etree.SubElement(parent,field)
    c.text=txt
    return(c)

def findAuth(name):
    name=name.strip('\n')
    y=name.find("|")
    auth= name[y:]
    v=len(auth)
    return[name[:y],auth[3:v-1]]
    

usedFiles=argv
     
#read parameters from paremeters.txt    
#params={}
#for lines in  open('parameters.txt','r'):
#    lines=lines.strip('\n')
#    x=lines.split(' ',1)
#    print(x)
#    params[x[0]]=x[1]
#print (params)
if argv[1]=='help':
    print('''
After the file name,  type the CSV read location,  MODS file locations
and the directory to write the results (This can be the same as the write location). 
Directories should be sepreated by a space. Use autocomplete (tab) to make life easier.
Valid input for mods Element is name or originInfo
Hit ctl-c anytime to exit
    
    ''')
    exit()
else:
    print("CSV read directory: {csvRead}".format(csvRead=argv[1]))
    print("XML read directory: {xmlRead}".format(xmlRead=argv[2]))
    print("XML Write directory: {xmlWrite}".format(xmlWrite=argv[3]))
    try:
        csvsource=open(argv[1],'r')
        reader=csv.reader(csvsource)
    except:
        print ("Invalid CSV location")
        exit()    
    
true=1
while true==True:
    readColumn=input("Column with Data> ")
    try:
        readColumn=int(readColumn)
    except:
        print("invalid column ID.  Id must be a number")
        continue
    modsField=input("Enter MODS element to be added as child of root> ")
    if modsField == 'name':
        modsSubField=input('Enter Child Mods Element> ')
        nameType=input('Enter type> ')
        role=input('Enter roleTerm Text> ')
        rolecodeID=input('Enter roleTerm code> ')
        print(''' You have selected {column} as read column
    {modsfield} as the element to be added
    {modssubfield} as a child field to be added
     {nametype} as the name type
     {role} as the role term and {rolecodeID} as roleTermCode'''.format(column=readColumn,modsfield=modsField,modssubfield=modsSubField, nametype=nameType, role=role,rolecodeID=rolecodeID))
        next=input('If this is correct press y to continue or any key to re enter data: ')
        if next=='y':
            myDict={rows[0]:rows[readColumn] for rows in reader}       
            break
      
        
        else:
            print ('try again')
            continue
    elif modsField=='originInfo':
        
        next=input('You have selected originInfo, with {readcolumn} as the place column and {readcolumn2} as the date column.  if this is correct, press y, or any other key to exit'.format(readcolumn=readColumn, readcolumn2=readColumn+1))
        if next=='y':
            try:
              myDict={rows[0]:rows[readColumn] for rows in reader}
              csvsource.close()
              csvsource=open(argv[1],'r')
              reader=csv.reader(csvsource)
              myDict2={rows[0]:rows[readColumn+1] for rows in reader}
              break         
            except:
                print ('invalid column id')
              
        else:
            exit()
        
    else:
        print("Input must be name or originInfo")
        continue
        
        
   

    
    
count=0      


#best practice is to register a namespace.        
etree.register_namespace('', 'http://www.loc.gov/mods/v3')
nb= {'mods':'http://www.loc.gov/mods/v3',}


for root, dirs, files in os.walk(argv[2]):
    for fileName in files:
        #assemble file name from root and filename
      fullpath=(os.path.join(root,fileName))
      
      if(fullpath[-3:])!='xml':continue
      else:
      #parse as xml
          tree=etree.parse(fullpath)
          
          base=tree.getroot()
          modsId=idFinder(fullpath)
          if modsId in myDict and myDict[modsId]!='':
             if modsField=='name':
                 z=myDict[modsId].split(";")
                 for things in z:
                      authName=findAuth(things)
                      if authName==['','']:continue 
                      
                      b=etree.SubElement(base,'{{http://www.loc.gov/mods/v3}}{modsField}'.format(modsField=modsField), attrib={'authority':authName[1],'type':nameType})
                      
                      addData(b,'{mods}{term}'.format(mods='{http://www.loc.gov/mods/v3}', term=modsSubField),authName[0])
                      if role !='':
                          
                           roleWrap=etree.SubElement(b,'{{http://www.loc.gov/mods/v3}}{modsField}'.format(modsField='role'))
                           roleterm=etree.SubElement(roleWrap,'{{http://www.loc.gov/mods/v3}}{modsField}'.format(modsField='roleTerm'), attrib={'authority':'marcrelator','type':'text'})
                           roleterm.text=role
                           rolecode=etree.SubElement(roleWrap,'{{http://www.loc.gov/mods/v3}}{modsField}'.format(modsField='roleTerm'), attrib={'authority':'marcrelator','type':'code'})
                           rolecode.text=rolecodeID
                      print ("Working: {terms} added to {filename}".format(terms=myDict[modsId], filename=fileName))
                      count=count+1
                      try:
                          tree.write('{filelocation}\\{filename}'.format(filelocation=argv[3],filename=fileName))
                      except:
			else: print ('no match on id{modsid}'.format(modsid=myDict[modsId]))
		  print ('Error:  Make sure write location directory exists')
             if modsField=='originInfo':
                  orginInfo=etree.SubElement(base,'{{http://www.loc.gov/mods/v3}}{modsField}'.format(modsField=modsField))
                  place=etree.SubElement(orginInfo,'{{http://www.loc.gov/mods/v3}}{modsField}'.format(modsField='place'))
                  placeterm=etree.SubElement(place,'{{http://www.loc.gov/mods/v3}}{modsField}'.format(modsField='placeTerm'), attrib={'type':'text'})
                  placeterm.text=myDict[modsId]
                  dateIssued=etree.SubElement(orginInfo,'{{http://www.loc.gov/mods/v3}}{modsField}'.format(modsField='dateIssued'))
                  dateSplit=(myDict2[modsId])
                  print (dateSplit)    
                  dateSplitlist=dateSplit.split()
                  dateIssued.text=dateSplitlist[0]
                  
                  count=count+1
                  print ("Working: {terms} added to {filename}".format(terms=myDict[modsId], filename=fileName))
                  try:
                      tree.write('{filelocation}\\{filename}'.format(filelocation=argv[3],filename=fileName),)
                  except:
                      print ('Error:  Make sure write location directory exists')
if count ==0:
    print ('No matches between Mods files and CSV file found.  Make sure the right Mods file directory is being used, and there is content in the column')
else:
    print ('Done! Files Processed: ', count)
csvsource.close()