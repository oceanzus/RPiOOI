#! /usr/bin/python3


#Tested in Python 3.7.3 on a Raspberry Pi Model 3B+.
#Tested in Python 3.7.4 in Windows 10.
#This script plots OOI CE09OSPM (McLane Moored Profiler) CTD  data at 24 hour intervals.
#For an example on how to make simultaneous requests for multiple datasets, look at CE01ISSM_MFN_TSDO.py

#Created by iblack (blackia@oregonstate.edu) with help from spearce, crisien, and cwingard.
#Some sections pulled from OOI M2M examples written by Sage and Friedrich Knuth.


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
interval = 60 * 24   #Frequency in minutes to request new data.
buffer = 5     #Number of minutes to add to the interval to account for the time it takes to make the request.
limit = backcast * 1  #Number of minutes of data to store in memory.

pad = 5  #Padding for plt.tight_layout()
windowtitle = 'T, S profiles @ 46.852 N, -124.982 E'  #Super title of your figure.

partial_url = 'https://ooinet.oceanobservatories.org/api/m2m/12576/sensor/inv/CE09OSPM/WFP01/03-CTDPFK000/telemetered/ctdpf_ckl_wfp_instrument'  #Partial URL (no times) of data request.
vartime = 'time'  #The OOI stream name of the time associated with the data you want.
var1 = 'ctdpf_ckl_seawater_pressure'  #The OOI stream name of one of the variables you want to plot on the y axis.
var2 = 'ctdpf_ckl_seawater_temperature'  #The OOI stream name of one of the variables you want to plot on the y axis.
var3 = 'practical_salinity'   #The OOI stream name of one of the variables you want to plot on the y axis.

timename = 'Datetime (UTC)'  #User-defined name of the time variable.
var1name = 'Pressure'  #User-defined name of var1.
var1units = 'dbars'   #User defined unit of var 1.
var2name = 'Temperature'
var2units = 'degC'
var3name = 'Salinity'
var3units = 'PSU'
#--------------------------------------------------#



class OOI():
    def __init__(self):  #Create empty lists at initialization.
        self.vartime = np.array([],dtype = 'datetime64')
        self.var1 = []
        self.var2 = []
        self.var3 = []
             
    def create_url(self,interval,buffer, partial_url): #Use the user set interval, buffer, and partial_url to create a M2M request URL.
        print('Generating M2M URL...')
        now = datetime.utcnow()    #Get the current time in UTC.
        past = now - timedelta(minutes=interval+buffer)     #Calculate what the time would be given the interval and buffer.
        now = now.strftime("%Y-%m-%dT%H:%M:%S.999Z")    #Craft time strings.
        past = past.strftime("%Y-%m-%dT%H:%M:%S.000Z") 
        timespan = "?beginDT=" + past + "&endDT=" + now  
        self.m2m_url = partial_url + timespan  #Craft the complete URL.
        print('M2M URL obtained.')

    def request_data(self, user, token):  #Request data using the previously generated URL.
        print('Processing request...')  
        r = requests.get(self.m2m_url,auth = (user,token))    
        data = r.json()                                     
        check = data['allURLs'][1] + '/status.txt'
        for i in range(1800):
            print('Checking request status...{:d}'.format(i),end = '\r')
            r = requests.get(check)
            if r.status_code == requests.codes.ok:
                print('\n')
                print('Request complete.')
                break
            else:
                time.sleep(1)  
                #plt.pause(1)  #Using plt.pause instead of time.sleep allows the plots to be interactive while data is being requested, however, this forces the plots to appear before the initial request.

        print('Sorting through contents...')        
        data_url = data['allURLs'][0] 
        multi_urls = requests.get(data_url).text  
        nclist = re.findall(r'(ooi/.*?.nc)', multi_urls)  
        for i in nclist:   
            if i.endswith('.nc') == False:  
                nclist.remove(i)
        for i in nclist:  
            try:
                float(i[-4]) == True
            except:
                nclist.remove(i)
        print('Sorting complete.')
        
        thredds_url = 'https://opendap.oceanobservatories.org/thredds/dodsC/' 
        opendap_url = os.path.join(thredds_url,str(nclist[0])) 
        opendap_url = opendap_url + '#fillmismatch'
        self.opendap_url = opendap_url
        print('Data available via OpenDAP URL.')

    def retrieve_data(self,vartime,var1,var2,var3,limit):  #Order: Time stream name, var1 stream name, var2 stream name, var3 stream name, rows to keep in arrays.
        print('Retrieving data...')
        prev_vartime = self.vartime  #Identify arrays for internal processing.
        prev_var1 = self.var1
        prev_var2 = self.var2
        prev_var3 = self.var3
       
        data = xr.open_dataset(self.opendap_url)  #Open the dataset. 
        vartime = data[vartime]   #Establish arrays based on the user defined stream name.
        var1 = data[var1]                                
        var2 = data[var2] 
        var3 = data[var3]
        print('Data collected.')

        vartime = np.append(prev_vartime,vartime)  #Append new data to old data.
        var1 = np.append(prev_var1,var1)
        var2 = np.append(prev_var2,var2)
        var3 = np.append(prev_var3,var3)   
        print('Data appended.')

        sortidx = vartime.argsort()     #Sort the data by time.
        vartime = vartime[sortidx[:]]
        var1 = var1[sortidx[:]]
        var2 = var2[sortidx[:]]
        var3 = var3[sortidx[:]]
        print('Data sorted.')

        vartime = np.array(vartime)
        vartime = pd.to_datetime(vartime,format='%Y%m%d %H:%M:%S', errors='coerce',utc = True)
        var1 = np.array(var1)
        var2 = np.array(var2)
        var3 = np.array(var3)

        newest = vartime[-1]
        oldest = vartime[0]
        memlim = newest - timedelta(minutes = limit)

        df = pd.DataFrame(vartime)
        trim = df[0] > memlim
        vartime = df.loc[trim].astype("datetime64[ns]")
        df = pd.DataFrame(var1)
        var1 = df.loc[trim]
        df = pd.DataFrame(var2)
        var2 = df.loc[trim]
        df = pd.DataFrame(var3)
        var3 = df.loc[trim]

        vartime = np.array(vartime[0]) 
        var1 = np.array(var1[0])
        var2 = np.array(var2[0])
        var3 = np.array(var3[0])

        self.vartime = vartime
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3
        
    def plot_data(self,interval,timename,var1name,var1units,var2name,var2units,var3name,var3units): #Plot the data.
        print('Plotting data...')
        
        ax1.clear()  #Clear the previous plot.
        tplot = ax1.scatter(x=self.vartime,y=self.var1,s=1,c=self.var2,cmap='jet')
        ax1.invert_yaxis()  #Invert the y-axis of the plot so it makes sense.
        ax1.set_title(var2name)  #Title the plot.
        ax1.set_ylabel(var1name + ' (' + var1units+ ') ')  #Give the y axis a label.
        ax1.xaxis.set_major_formatter(fmt) 
        ax1.tick_params(labelrotation=15)
        ax1.set_xlim(left = self.vartime[0],right=self.vartime[-1])

        ax2.clear()
        splot = ax2.scatter(x=self.vartime,y=self.var1,s=1,c=self.var3,cmap='jet')
        ax2.invert_yaxis()  #Invert the y-axis of the plot so it makes sense.
        ax2.set_title(var3name)  #Title the plot.
        ax2.set_ylabel(var1name + ' (' + var1units+ ') ')   #Give the y axis a label.
        ax2.set_xlabel(timename)  #Give the x axis a label.
        ax2.xaxis.set_major_formatter(fmt) 
        ax2.tick_params(labelrotation=15)
        ax2.set_xlim(left = self.vartime[0],right=self.vartime[-1])
        
        ctrlfstr = 'Use CTRL + F to enter or exit fullscreen.'
        textbox = ax1.text(0.01,0.01,ctrlfstr,fontsize=8,transform = plt.gcf().transFigure,color = 'k')

        fig.colorbar(tplot,cax=cax1,label=var2units)  #Assign the temperature plot a colorbar.
        fig.colorbar(splot,cax=cax2,label=var3units)
        print('Plot available. Waiting for %d minutes before initiating next request.' %(interval))
        plt.pause(interval*60)

           
def animate(j): 
    print('Setting up request for loop number %d.' % (j))
    OOI.create_url(interval,buffer,partial_url)
    OOI.request_data(user,token)
    OOI.retrieve_data(vartime,var1,var2,var3,limit)
    OOI.plot_data(interval,timename,var1name,var1units,var2name,var2units,var3name,var3units)
    print('Loop resetting.')

print('Setting up initial request.')      
root = tkinter.Tk()  #Create a Tk object to get the screen dimensions.
width = root.winfo_screenwidth()  #Define the screen width in pixels.
height = root.winfo_screenheight()  #Define the screen height in pixels
dpi = 100  #Define the number of pixes per inch.
root.destroy()  #Remove the Tk object because it is annoying.

fig = plt.figure(figsize=(width/dpi,height/dpi),facecolor = 'gray',edgecolor = 'black')
[ax1,cax1],[ax2,cax2] = fig.subplots(nrows=2,ncols=2,gridspec_kw={"width_ratios":[50,1]})  #Add subplots
fmt = mdates.DateFormatter('%Y-%m-%d %H:%M')  #Define how the dates are displayed.
plt.tight_layout(pad = pad)
fig.canvas.set_window_title(windowtitle)  #Set the window title.
fig.suptitle(windowtitle)  #Add a title for the figure.


OOI = OOI()
OOI.create_url(backcast,buffer,partial_url)
OOI.request_data(user,token)
OOI.retrieve_data(vartime,var1,var2,var3,limit)
OOI.plot_data(interval,timename,var1name,var1units,var2name,var2units,var3name,var3units)
print('Initiating animation loop.')

ani = animation.FuncAnimation(fig,animate,interval = 1000) #After the plt.pause, restart the animation after 1 second.
plt.show(block=False)  #Show the plot, but don't block the script.


