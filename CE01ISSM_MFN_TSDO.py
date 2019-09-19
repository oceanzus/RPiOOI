#! /usr/bin/python3
import os , sys, time , string , math , requests , re , tkinter , matplotlib
import numpy as np , pandas as pd, xarray as xr, datetime as dt
import matplotlib.pyplot as plt , matplotlib.animation as animation , matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from dateutil.tz import *
from datetime import datetime , timedelta, tzinfo
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#--------------------------------------------------#
user = 'OOIAPI-BCJPAYP2KUVXFX'  #OOI API username.
token = 'D3HV2X0XH1O'   #OOI API token.
backcast = 12    #Number of hours to initially display.
interval = 6    #Frequency in hours to request new data over the last specified interval.
pointrange = 15000  #The maximum number of rows to keep in an array.

pad = 5  #Padding for plt.tight_layout()
windowtitle = 'T,S,DO near bottom @ 44.66 N, -124.095 E'


partial_url_1 = 'https://ooinet.oceanobservatories.org/api/m2m/12576/sensor/inv/CE01ISSM/MFD37/03-CTDBPC000/telemetered/ctdbp_cdef_dcl_instrument'
partial_url_2 = 'https://ooinet.oceanobservatories.org/api/m2m/12576/sensor/inv/CE01ISSM/MFD37/03-DOSTAD000/telemetered/dosta_abcdjm_ctdbp_dcl_instrument'  #Partial URL (no times) of data request.
vartime_1 = 'time'  #The stream name of the time associated with the data you want.
vartime_2 = 'time'
var1 = 'temp'  #The stream name of one of the variables you want to plot on the y axis.
var2 = 'practical_salinity'  #The stream name of one of the variables you want to plot on the y axis.
var3 = 'dissolved_oxygen'   #The stream name of one of the variables you want to plot on the y axis.
timename = 'Datetime (UTC)'  #Name of the time variable.
var1name = 'Temperature'  #Name of var1.
var1units = 'degC'   #Unit of var 1.
var2name = 'Salinity'
var2units = 'PSU'
var3name = 'Oxygen Concentration'
var3units = 'umol/kg'
#--------------------------------------------------#

class OOI():
    def __init__(self): 
        self.vartime_1 = np.array([],dtype = 'datetime64')
        self.vartime_2 = np.array([],dtype = 'datetime64')
        self.var1 = []
        self.var2 = []
        self.var3 = []
               
    def create_url(self,interval, partial_url_1, partial_url_2):  #Order: Number of hours to request from current time, partial url identified earlier.
        now = datetime.utcnow()  
        past = now - timedelta(hours=interval)
        now = now.strftime("%Y-%m-%dT%H:%M:%S.999Z")  
        past = past.strftime("%Y-%m-%dT%H:%M:%S.000Z") 
        timespan = "?beginDT=" + past + "&endDT=" + now  
        self.m2m_url_1 = partial_url_1 + timespan
        self.m2m_url_2 = partial_url_2 + timespan
        print('Created M2M URL.')

    def request_data(self, user, token):  #Order: OOI API User, OOI API Token
        r_1 = requests.get(self.m2m_url_1,auth= (user,token))    
        data_1 = r_1.json()                                     
        check_1 = data_1['allURLs'][1] + '/status.txt'

        r_2 = requests.get(self.m2m_url_2,auth= (user,token))    
        data_2 = r_2.json()                                     
        check_2 = data_2['allURLs'][1] + '/status.txt'
        
        print ('Processing request...')  
        for i in range(1800):
            r_1 = requests.get(check_1)
            time.sleep(0.5)
            r_2 = requests.get(check_2)
            if r_1.status_code == requests.codes.ok and r_2.status_code == requests.codes.ok:
                print('Request complete.')
                break
            else: 
                time.sleep(0.5)
                
        data_url_1 = data_1['allURLs'][0] 
        multi_urls_1 = requests.get(data_url_1).text  
        nclist_1 = re.findall(r'(ooi/.*?.nc)', multi_urls_1)  
        for i in nclist_1:   
            if i.endswith('.nc') == False:  
                nclist_1.remove(i)
        for i in nclist_1:  
            try:
                float(i[-4]) == True
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
                
        thredds_url = 'https://opendap.oceanobservatories.org/thredds/dodsC/'
        
        opendap_url_1 = os.path.join(thredds_url,str(nclist_1[0])) 
        opendap_url_1 = opendap_url_1 + '#fillmismatch'
        self.opendap_url_1 = opendap_url_1

        opendap_url_2 = os.path.join(thredds_url,str(nclist_2[0])) 
        opendap_url_2 = opendap_url_2 + '#fillmismatch'
        self.opendap_url_2 = opendap_url_2
        
        print('OpenDAP URLs available.')

    def retrieve_data(self,vartime_1,vartime_2,var1,var2,var3,pointrange):  #Order:  stream name time 1, stream name time 2,  var1 stream name, var2 stream name, var3 stream name, rows to keep in arrays.
        prev_vartime_1 = self.vartime_1
        prev_vartime_2 = self.vartime_2
        prev_var1 = self.var1
        prev_var2 = self.var2
        prev_var3 = self.var3
       
        data_1 = xr.open_dataset(self.opendap_url_1)
        vartime_1= data_1[vartime_1] 
        var1 = data_1[var1]                                
        var2 = data_1[var2]

        data_2 = xr.open_dataset(self.opendap_url_2)
        vartime_2= data_2[vartime_2]                           
        var3 = data_2[var3]
        print('Data collected.')

        vartime_1 = np.append(vartime_1,prev_vartime_1)
        vartime_2 = np.append(vartime_2,prev_vartime_2)
        var1 = np.append(var1,prev_var1)
        var2 = np.append(var2,prev_var2)
        var3 = np.append(var3,prev_var3)
        
        print('Data appended.')
        
        if vartime_2.shape[0] > pointrange:  #If the array gets too 
            print('Trimming arrays.')
            vartime_1 = vartime_1[-pointrange:]
            vartime_2 = vartime_2[-pointrange:]
            var1 = var1[-pointrange:]
            var2 = var2[-pointrange:]
            var3 = var3[-pointrange:]
        else: 
            print('No trimming required.')

        self.vartime_1 = vartime_1
        self.vartime_2 = vartime_2
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3
        
    def plot_data(self,timename,var1name,var1units,var2name,var2units,var3name,var3units):  #Order, variable names and units.
        print('Plotting data.')
        plotvartime_1 = np.array(self.vartime_1,dtype = 'datetime64')
        plotvartime_1 = pd.to_datetime(plotvartime_1,format='%Y%m%d %H:%M:%S', errors='coerce',utc = True)

        plotvartime_2 = np.array(self.vartime_2,dtype = 'datetime64')
        plotvartime_2 = pd.to_datetime(plotvartime_1,format='%Y%m%d %H:%M:%S', errors='coerce',utc = True)

        plotvar1 = np.array(self.var1)
        plotvar2 = np.array(self.var2)
        plotvar3 = np.array(self.var3)

        ax1.clear()
        ax1.plot(plotvartime_1,plotvar1,'r')  
        ax1.plot(plotvartime_1[-1],plotvar1[-1],'k+',markersize=3000,alpha=0.3)
        ax1.set_title(var1name) 
        ax1.set_ylabel(var1units)  
        ax1.xaxis.set_major_formatter(fmt) 
        ax1.tick_params(labelrotation=0)
        ax2.set_xlim(left = plotvartime_1[0])


        ax2.clear()
        ax2.plot(plotvartime_1,plotvar2,'k')
        ax2.plot(plotvartime_1[-1],plotvar2[-1],'k+',markersize=3000,alpha=0.3)
        ax2.set_title(var2name)
        ax2.set_ylabel(var2units)
        ax2.xaxis.set_major_formatter(fmt)
        ax2.tick_params(labelrotation=0)
        ax2.set_xlim(left = plotvartime_1[0])


        ax3.clear()
        ax3.plot(plotvartime_2,plotvar3,'b')
        ax3.plot(plotvartime_2[-1],plotvar3[-1],'k+',markersize=3000,alpha=0.3)
        ax3.set_title(var3name)
        ax3.set_ylabel(var3units)
        ax3.xaxis.set_major_formatter(fmt)
        ax3.tick_params(labelrotation=0)
        ax3.set_xlabel(timename)
        ax3.set_xlim(left = plotvartime_2[0])

        ctrlfstr = 'Use CTRL + F to enter or exit fullscreen.'
        textbox = ax1.text(0.05,0.975,ctrlfstr,fontsize=8,transform = plt.gcf().transFigure,color = 'k')
                 
def animate(j): 
    print('Setting up request for loop({:d}).'.format(j))
    OOI.create_url(interval,partial_url_1,partial_url_2)
    OOI.request_data(user,token)
    OOI.retrieve_data(vartime_1,vartime_2,var1,var2,var3,pointrange)
    OOI.plot_data(timename,var1name,var1units,var2name,var2units,var3name,var3units)
    print('Next request for data in {:2d} hour(s).'.format(interval))

print('Setting up initial request.')      
root = tkinter.Tk()  #Create a Tk object to get the screen dimensions.
width = root.winfo_screenwidth()  #Define the screen width in pixels.
height = root.winfo_screenheight()  #Define the screen height in pixels
dpi = 100  #Define the number of pixes per inch.
fig = plt.figure(figsize=(width/dpi,height/dpi),facecolor = 'gray',edgecolor = 'black')  
ax1,ax2,ax3 = fig.subplots(3,1)  #Add subplots
fmt = mdates.DateFormatter('%m-%d %H:%M')  #Define how the dates are displayed.
plt.tight_layout(pad = pad)
fig.canvas.set_window_title(windowtitle)  #Set the window title.
fig.suptitle(windowtitle)  #Add a title for the figure.
root.destroy()  #Remove the Tk object because it is annoying.

OOI = OOI()
OOI.create_url(backcast,partial_url_1,partial_url_2)
OOI.request_data(user,token)
OOI.retrieve_data(vartime_1,vartime_2,var1,var2,var3,pointrange)
OOI.plot_data(timename,var1name,var1units,var2name,var2units,var3name,var3units)
plt.draw()
print('Waiting for {:d} hour(s) before initiating next request.'.format(interval))
plt.pause(interval*60*60)
ani = animation.FuncAnimation(fig,animate,interval = interval * 60 * 60 * 1000)
plt.show()

