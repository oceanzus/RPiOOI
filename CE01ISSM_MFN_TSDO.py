#! /usr/bin/python3

#Tested in Python 3.7.3 on a Raspberry Pi Model 3B+.
#Tested in Python 3.7.4 in Windows 10.

#This script plots OOI CE01ISSM MFN (Multi-Function Node) CTD and oxygen data asynchronously.
#It will initially plot the previous 7 days and then will request new data every 24 hours.

#Created by iblack (blackia@oregonstate.edu) with help from spearce, crisien, and cwingard.
#Some sections pulled from OOI M2M examples written by Friedrich Knuth and Sage.

import os , sys, time , string , math , requests , re , tkinter , matplotlib
import numpy as np , pandas as pd, xarray as xr, datetime as dt
import matplotlib.pyplot as plt , matplotlib.animation as animation , matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from dateutil.tz import *
from datetime import datetime , timedelta
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()



#--------------------------------------------------#
user = 'OOIAPI-BCJPAYP2KUVXFX'  #OOI API username.
token = 'D3HV2X0XH1O'   #OOI API token.

backcast = 60 * 24 * 7   #Number of minutes to initially display.
interval =  60 * 24 #Frequency in minutes to request new data.
buffer = 5     #Number of minutes to add to the interval to account for the time it takes to make the request.
limit = backcast * 7  #Number of minutes of data to store in memory. Should be greater or equal to the backcast time. Effectively becomes the x-axis limit.

pad = 5  #Padding for plt.tight_layout()
windowtitle = 'T, S, DO near bottom @ 44.66 N, -124.095 E'  #Title of figure.

partial_url_1 = 'https://ooinet.oceanobservatories.org/api/m2m/12576/sensor/inv/CE01ISSM/MFD37/03-CTDBPC000/telemetered/ctdbp_cdef_dcl_instrument'  #Partial URL (no times) of data request.
partial_url_2 = 'https://ooinet.oceanobservatories.org/api/m2m/12576/sensor/inv/CE01ISSM/MFD37/03-DOSTAD000/telemetered/dosta_abcdjm_ctdbp_dcl_instrument'  #Partial URL (no times) of data request.

vartime_1 = 'time'  #The OOI stream name of the time associated with the data you want.
vartime_2 = 'time'
var1 = 'temp'  #The OOI stream name of one of the variables you want to plot on the y axis.
var2 = 'practical_salinity'  #The OOI stream name of one of the variables you want to plot on the y axis.
var3 = 'dissolved_oxygen'   #The OOI stream name of one of the variables you want to plot on the y axis.

timename = 'Datetime (UTC)'  #User defined name of the time variable.
var1name = 'Temperature'  #User defined name of var1.
var1units = 'degC'   #User defined unit of var 1.
var2name = 'Salinity'
var2units = 'PSU'
var3name = 'Oxygen Concentration'
var3units = 'umol/kg'
#--------------------------------------------------#



class OOI():
    def __init__(self):  #Create empty lists at initialization.
        self.vartime_1 = np.array([],dtype = 'datetime64')
        self.vartime_2 = np.array([],dtype = 'datetime64')
        self.var1 = []
        self.var2 = []
        self.var3 = []
             
    def create_url(self,interval,buffer, partial_url_1, partial_url_2): #Use the user set interval, buffer, and partial_url to create a M2M request URL.
        print('Generating M2M URL...')
        now = datetime.utcnow()    #Get the current time in UTC.
        past = now - timedelta(minutes=interval+buffer)     #Calculate what the time would be given the interval and buffer.
        now = now.strftime("%Y-%m-%dT%H:%M:%S.999Z")    #Craft time strings.
        past = past.strftime("%Y-%m-%dT%H:%M:%S.000Z") 
        timespan = "?beginDT=" + past + "&endDT=" + now  
        self.m2m_url_1 = partial_url_1 + timespan  #Craft the complete URL.
        self.m2m_url_2 = partial_url_2 + timespan  #Craft the complete URL.
        print('M2M URL obtained.')

    def request_data(self, user, token):  #Request data using the previously generated URL.
        print('Processing request...')  
        r_1 = requests.get(self.m2m_url_1,auth = (user,token))    #Authorization is the user-defined API username and token.
        data_1 = r_1.json()                                     
        check_1 = data_1['allURLs'][1] + '/status.txt'
        time.sleep(1)
        r_2 = requests.get(self.m2m_url_2,auth = (user,token))    
        data_2 = r_2.json()                                     
        check_2 = data_2['allURLs'][1] + '/status.txt'
        for i in range(1800):
            print('Checking request status...{:d}'.format(i),end = '\r')
            r_1 = requests.get(check_1)  #Check to see if the request is complete.
            time.sleep(0.5)
            r_2 = requests.get(check_2)
            if r_1.status_code == requests.codes.ok and r_2.status_code == requests.codes.ok:
                print('Request complete.')
                break
            else:
                time.sleep(0.5)  
                #plt.pause(0.5)  #Using plt.pause instead of time.sleep allows the plots to be interactive while data is being requested, however, this forces the plots to appear before the initial request.

        print('Sorting through contents...')        
        data_url_1 = data_1['allURLs'][0] 
        multi_urls_1 = requests.get(data_url_1).text  
        nclist_1 = re.findall(r'(ooi/.*?.nc)', multi_urls_1)  
        for i in nclist_1:   #Given the available urls.
            if i.endswith('.nc') == False:  # If it isn't a .nc, get rid of it.
                nclist_1.remove(i)
        for i in nclist_1:  
            try:
                float(i[-4]) == True  #If the digit before the .nc isn't a number (i.e. date value), get ride of it.
            except:
                nclist_1.remove(i)

        data_url_2 = data_2['allURLs'][0] 
        multi_urls_2 = requests.get(data_url_2).text  
        nclist_2 = re.findall(r'(ooi/.*?.nc)', multi_urls_2)  
        for i in nclist_2:   
            if i.endswith('.nc') == False:  
                nclist_2.remove(i)
        for i in nclist_2:  
            try:
                float(i[-4]) == True
            except:
                nclist_2.remove(i)                
        print('Sorting complete.')
        
        thredds_url = 'https://opendap.oceanobservatories.org/thredds/dodsC/' 
        opendap_url_1 = os.path.join(thredds_url,str(nclist_1[0])) #Append with the opendap url to get data.
        opendap_url_1 = opendap_url_1 + '#fillmismatch'  #Add this identifier so we don't get any errors.
        self.opendap_url_1 = opendap_url_1
        
        opendap_url_2 = os.path.join(thredds_url,str(nclist_2[0])) 
        opendap_url_2 = opendap_url_2 + '#fillmismatch'
        self.opendap_url_2 = opendap_url_2
        print('Data available via OpenDAP URL.')

    def retrieve_data(self,vartime_1,vartime_2,var1,var2,var3,limit):  #Get the data.
        print('Retrieving data...')
        prev_vartime_1 = self.vartime_1  #Identify arrays for internal processing.
        prev_vartime_2 = self.vartime_2
        prev_var1 = self.var1
        prev_var2 = self.var2
        prev_var3 = self.var3
       
        data = xr.open_dataset(self.opendap_url_1)  #Open the dataset. 
        vartime_1 = data[vartime_1]   #Establish arrays based on the user defined stream name.
        var1 = data[var1]                                
        var2 = data[var2] 
           
        data = xr.open_dataset(self.opendap_url_2)
        vartime_2 = data[vartime_2]
        var3 = data[var3]
        print('Data collected.')

        vartime_1 = np.append(prev_vartime_1,vartime_1)  #Append new data to old data.
        vartime_2 = np.append(prev_vartime_1,vartime_2)
        var1 = np.append(prev_var1,var1)
        var2 = np.append(prev_var2,var2)
        var3 = np.append(prev_var3,var3)   
        print('Data appended.')

        sortidx = vartime_1.argsort()     #Sort the data by time.
        vartime_1 = vartime_1[sortidx[:]] 
        var1 = var1[sortidx[:]] #Sort the other data arrays based on the time array index.
        var2 = var2[sortidx[:]]

        sortidx = vartime_2.argsort()  
        vartime_2 = vartime_2[sortidx[:]] 
        var3 = var3[sortidx[:]]
        print('Data sorted.')

        vartime_1 = np.array(vartime_1)  #Make sure everything is in an array.
        vartime_1 = pd.to_datetime(vartime_1,format='%Y%m%d %H:%M:%S', errors='coerce',utc = True)  #Pandas is smart enough to know the date of origin.
        vartime_2 = np.array(vartime_2)
        vartime_2 = pd.to_datetime(vartime_2,format='%Y%m%d %H:%M:%S', errors='coerce',utc = True)
        var1 = np.array(var1)
        var2 = np.array(var2)
        var3 = np.array(var3)

        newest = vartime_1[-1]  #Remove data that is outside the limit.
        oldest = vartime_1[0]
        memlim = newest - timedelta(minutes = limit)
        df = pd.DataFrame(vartime_1)
        trim = df[0] > memlim
        vartime_1 = df.loc[trim].astype("datetime64[ns]")
        df = pd.DataFrame(var1)
        var1 = df.loc[trim]
        df = pd.DataFrame(var2)
        var2 = df.loc[trim]

        newest = vartime_2[-1]
        oldest = vartime_2[0]
        memlim = newest - timedelta(minutes = limit)
        df = pd.DataFrame(vartime_2)
        trim = df[0] > memlim
        vartime_2 = df.loc[trim].astype("datetime64[ns]")
        df = pd.DataFrame(var3)
        var3 = df.loc[trim]

        vartime_1 = np.array(vartime_1[0]) #Really make sure everything is in an array.
        vartime_2 = np.array(vartime_2[0]) 
        var1 = np.array(var1[0])
        var2 = np.array(var2[0])
        var3 = np.array(var3[0])

        self.vartime_1 = vartime_1
        self.vartime_2 = vartime_2
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3
        
    def plot_data(self,interval,timename,var1name,var1units,var2name,var2units,var3name,var3units):  #Plot the data.
        print('Plotting data...')
        
        ax1.clear()  #Clear the previous plot.
        ax1.plot(self.vartime_1,self.var1,'r')  #Plot the data for var1.
        ax1.plot(self.vartime_1[-1],self.var1[-1],'k+',markersize=3000,alpha=0.3)  #Pseudo-plot crosshairs on last point.
        ax1.set_title(var1name) 
        ax1.set_ylabel(var1units)  
        ax1.xaxis.set_major_formatter(fmt) 
        ax1.tick_params(labelrotation=0)
        ax1.set_xlim(left = self.vartime_1[0])

        ax2.clear()
        ax2.plot(self.vartime_1,self.var2,'k')
        ax2.plot(self.vartime_1[-1],self.var2[-1],'k+',markersize=3000,alpha=0.3)
        ax2.set_title(var2name)
        ax2.set_ylabel(var2units)
        ax2.xaxis.set_major_formatter(fmt)
        ax2.tick_params(labelrotation=0)
        ax2.set_xlim(left = self.vartime_1[0])
     
        ax3.clear()
        ax3.plot(self.vartime_2,self.var3,'b')     
        ax3.plot(self.vartime_2[-1],self.var3[-1],'k+',markersize=3000,alpha=0.3)
        ax3.set_title(var3name)
        ax3.set_ylabel(var3units)
        ax3.xaxis.set_major_formatter(fmt)
        ax3.tick_params(labelrotation=0)
        ax3.set_xlabel(timename)
        ax3.set_xlim(left = self.vartime_1[0])
        
        ctrlfstr = 'Use CTRL + F to enter or exit fullscreen.'
        textbox = ax1.text(0.01,0.01,ctrlfstr,fontsize=8,transform = plt.gcf().transFigure,color = 'k')
        
        print('Plot available. Waiting for %d minutes before initiating next request.' %(interval))
        plt.pause(interval*60)
                 
def animate(j): 
    print('Setting up request for loop number %d.' % (j))
    OOI.create_url(interval,buffer,partial_url_1,partial_url_2)
    OOI.request_data(user,token)
    OOI.retrieve_data(vartime_1,vartime_2,var1,var2,var3,limit)
    OOI.plot_data(interval,timename,var1name,var1units,var2name,var2units,var3name,var3units)
    print('Loop resetting.')



print('Setting up initial request.')      
root = tkinter.Tk()  #Create a Tk object to get the screen dimensions.
width = root.winfo_screenwidth()  #Define the screen width in pixels.
height = root.winfo_screenheight()  #Define the screen height in pixels
dpi = 100  #Define the number of pixes per inch.
root.destroy()  #Remove the Tk object because it is annoying.
fig = plt.figure(figsize=(width/dpi,height/dpi),facecolor = 'gray',edgecolor = 'black')
ax1,ax2,ax3 = fig.subplots(3,1)  #Add subplots
fmt = mdates.DateFormatter('%Y-%m-%d %H:%M')  #Define how the dates are displayed.
plt.tight_layout(pad = pad)
fig.canvas.set_window_title(windowtitle)  #Set the window title.
fig.suptitle(windowtitle)  #Add a title for the figure.

OOI = OOI()
OOI.create_url(backcast,buffer,partial_url_1,partial_url_2)
OOI.request_data(user,token)
OOI.retrieve_data(vartime_1,vartime_2,var1,var2,var3,limit)
OOI.plot_data(interval,timename,var1name,var1units,var2name,var2units,var3name,var3units)

print('Initiating animation loop.')
ani = animation.FuncAnimation(fig,animate,interval = 1000)
plt.show(block=False)  #Show the plot, but don't block the script.


