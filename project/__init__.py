# project/__init__.py

import os  # new
from flask import Flask,jsonify,request
from flask_restx import Resource, Api
import csv
import json
from flask_cors import CORS
from configparser import ConfigParser
import subprocess
import sys
from glob import glob
from datetime import date, timedelta
from datetime import datetime

# instantiate the app
app = Flask(__name__)
cors = CORS(app)
api = Api(app)

import xml.etree.ElementTree as ET
tree = ET.parse("E:\\Portal_Automation_Server\\nginx\\html\\Assets\\Config\\Config_xmlfile.xml")
root = tree.getroot()
print(root.tag)


class Readcsv(Resource):
    
    def csvtojsonconvert(file): 
        f= open(file,'r')
        csvReader = csv.DictReader(f)
        #rootitem = str(file)
        rootitem = "details"
       
        arr= { rootitem: []}
        arr["path"] = str(file)
        
        for csvRow in csvReader:
           arr[rootitem].append(csvRow)
        s= json.dumps(arr)       
        return s;
    
    def get(self, portal,fromdate,todate):
        print(portal)
        all_csv_files = Readcsv.getallcsvfiles(portal,fromdate,todate)
       # print(all_csv_files)
        outp ={}
        data = "data"
        outp= {data: []}
     
        #outp["data"]
        
        for file in range(len(all_csv_files)):
            output = Readcsv.csvtojsonconvert(all_csv_files[file])
            print(output)
            print(json.loads(output))
            print(type(outp))
            outp[data].append(json.loads(output))
            print(type(outp))
        return outp
    
    def getallcsvfiles(portal,fromdate,todate):
         delta = timedelta(days=1)
         all_files =[]
         startdate = datetime.strptime(fromdate, "%d%m%Y").date();
         enddate = datetime.strptime(todate, "%d%m%Y").date();
         while startdate <= enddate:
             for portalname in root.findall('Portal'):
                 if (portal == "khs") & (portalname.find("Name").text == "KHS"):               
                     PATH = portalname.find("Destination_Dir").text + "/Run/" + str(startdate.strftime("%d-%m-%Y")).replace('-','')
                     print(PATH)
                 elif (portal == "krones") & (portalname.find("Name").text == "Krones"):
                     PATH = portalname.find("Destination_Dir").text + "/Run/" + str(startdate.strftime("%d-%m-%Y")).replace('-','')       
             EXT = "*.csv"
             all_csv_files = [file
                for path, subdir, files in os.walk(PATH)
                for file in glob(os.path.join(path, EXT))]             
             print(type(all_csv_files))
             all_files.extend(all_csv_files)
             startdate += delta
         return all_files;

@app.route('/writecsv', methods=['PUT'])
def setName():
    if request.method=='PUT':
        posted_data = request.get_json()
        data = posted_data['data']
        num_files = len(data)
        print(num_files)
        count = 0
        while (count < num_files):
            filename= data[count].get("path")
            get_data = data[count].get("details")
            print(filename)
            
            data_file = open(filename, 'w')
            csv_writer = csv.writer(data_file,sys.stdout, lineterminator='\n') 
                
            count1 = 0
            for emp in get_data: 
                            if count1 == 0: 
                                header = emp.keys() 
                                csv_writer.writerow(header) 
                            count1 += 1 
                            csv_writer.writerow(emp.values()) 
            data_file.close()
            count = count + 1
    return jsonify(str(data))


class Runbat(Resource): 
  
    def get(self,portal): 
        for portalname in root.findall('Portal'):
            if (portal == "khs") & (portalname.find("Name").text == "KHS"):
                filepath = portalname.find("Runjobpath").text
            elif (portal == "krones") & (portalname.find("Name").text == "Krones"):
                filepath = portalname.find("Runjobpath").text  + "\Test_Portal_Automation.bat"
        #filepath = configur.get('portals_path','batfile_path') + "\Test_Portal_Automation.bat"
        #subp = subprocess.Popen('E:\\Test_Portal_Automation\\Config\\Test_Portal_Automation.bat', shell=True)
        subp = subprocess.Popen(filepath, shell=True)
        subp.communicate()
        return jsonify({'message': 'success'})  
    


api.add_resource(Readcsv, '/readcsv/<portal>/<fromdate>/<todate>')
api.add_resource(Runbat, '/Runbat/<portal>') 