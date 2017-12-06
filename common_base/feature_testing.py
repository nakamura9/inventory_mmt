from django.core.exceptions import *
import pandas as pd 
from inv import models as inv_models
machines = ["01", "02", "03"]
sections = []
subassys = []
subunits = []
components = []


class DummyMachine():
    def __init__(self, name, pk):
        self.name = name
        self.pk = pk

class DummySection():
    def __init__(self, name, pk):
        global sections
        self.name = name
        if pk[:2] in machines:
            self.machine = pk[:2]
            sections.append(pk)
        else:
            raise ValueError()

class DummySubUnit():
    def __init__(self, name, pk):
        global subunits
        self.name = name
        if pk[:2] in machines:
            self.machine = pk[:2]
        else:
            raise ValueError()
        if pk[:4] in sections:
            self.section = pk[:4]
        else:
            raise ValueError()
        subunits.append(pk)


class DummySubAssembly():
    def __init__(self, name,  pk):
        global subassys
        self.name = name
        if pk[:2] in machines:
            self.machine = pk[:2]
        else:
            raise ValueError()
        if pk[:4] in sections:
            self.section = pk[:4]
        else:
            raise ValueError()
        if pk[:6] in subunits:
            self.subunit = pk[:6]
        else:
            raise ValueError()
        subassys.append(pk)

class DummyComponent():

    def __init__(self, name, pk):
        global components
        self.name = name
        if pk[:2] in machines:
            self.machine = pk[:2]
        else:
            raise ValueError()
        if pk[:4] in sections:
            self.section = pk[:4]
        else:
            raise ValueError()
        if pk[:6] in subunits:
            self.subunit = pk[:6]
        else:
            raise ValueError()
        if pk[:8] in subassys:
            self.subassy = pk[:8]
        else:
            raise ValueError()
        components.append(pk)


def parse_file(file_name):
    global components
    fil = pd.read_csv(file_name)
    
    print "Starting..."
    i=0
    print fil.iloc[0,0]
    # test to make sure errors dont run aaway with it
    length = fil.shape[0]

    while i < length:
        try:
            #makes sure the number can be converted to a string
            while True:
                try:
                    num = int(fil.iloc[i,0])
                    break
                except:
                    print "Error: %s row: %d: There is missing data in this row" % (str(fil.iloc[i,0]), i)
                    i += 1
                
            if len(str(num)) % 2 != 0:
                id_string =  "0" + str(num)
            else:
                id_string = str(num)


            name = str(fil.iloc[i,1])
            name = "".join( [ j if ord(j) < 128 else ' ' for j in name] )
            
            if len(id_string) == 4:
                #Section 
                DummySection(name, id_string)
            
            elif len(id_string) == 6:
                #Subt Unit
                DummySubUnit(name, id_string)

            elif len(id_string) == 8:
                #Sub assembly
                DummySubAssembly(name, id_string)

            elif len(id_string) == 10:
                #Component
                DummyComponent(name, id_string)
            i = i +  1

        except ValueError as e:
            print "Error: row %d: %s with id: %s" % (i, str(e), id_string)
            i += 1

        except IOError as e:
            print "Error: row %d: %s" % (i, str(e))
        
        except IndexError:
            print "Finished processing"
            break
    
    print components
