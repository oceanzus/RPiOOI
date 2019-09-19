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
backcast = 72    #Number of hours to initially display.
interval = 8   #Frequency in hours to request new data over the last number of hours determined by interval.
pointrange = 20000  #The maximum number of rows to keep in an array. Assists with limiting strain on RPi memory.

pad = 5  #Padding for plt.tight_layout()
windowtitle = 'T,S profiles @ 46.852 N, -124.982 E'


partial_url = 'https://ooinet.oceanobservatories.org/api/m2m/12576/sensor/inv/CE09OSPM/WFP01/03-CTDPFK000/telemetered/ctdpf_ckl_wfp_instrument'  #Partial URL (no times) of data request.
vartime = 'time'  #The stream name of the time associated with the data you want.
var1 = 'ctdpf_ckl_seawater_pressure'  #The stream name of one of the variables you want to plot on the y axis.
var2 = 'ctdpf_ckl_seawater_temperature'  #The stream name of one of the variables you want to plot on the y axis.
var3 = 'practical_salinity'   #The stream name of one of the variables you want to plot on the y axis.

timename = 'Datetime (UTC)'  #Name of the time variable.
var1name = 'Pressure'  #Name of var1.
var1units = 'dbars'   #Unit of var 1.
var2name = 'Temperature'
var2units = 'degC'
var3name = 'Salinity'
var3units = 'PSU'
#--------------------------------------------------#

class OOI():
    def __init__(self): 
        self.vartime = np.array([],dtype = 'datetime64')
        self.var1 = []
        self.var2 = []
        self.var3 = []
               
    def create_url(self,interval, partial_url):  #Order: Number of hours to request from current time, partial url identified earlier.
        now = datetime.utcnow()  
        past = now - timedelta(hours=interval)
        now = now.strftime("%Y-%m-%dT%H:%M:%S.999Z")  
        past = past.strftime("%Y-%m-%dT%H:%M:%S.000Z") 
        timespan = "?beginDT=" + past + "&endDT=" + now  
        self.m2m_url = partial_url + timespan
        print('Created M2M URL.')

    def request_data(self, user, token):  #Order: OOI API User, OOI API Token
        r = requests.get(self.m2m_url,auth= (user,token))    
        data = r.json()                                     
        check = data['allURLs'][1] + '/status.txt'
        print ('Processing request...')  
        for i in range(1800):
            r = requests.get(check)
            if r.status_code == requests.codes.ok:
                print('Request complete.')
                break
            else: 
                time.sleep(1)    
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
                
        thredds_url = 'https://opendap.oceanobservatories.org/thredds/dodsC/' 
        opendap_url = os.path.join(thredds_url,str(nclist[0])) 
        opendap_url = opendap_url + '#fillmismatch'
        self.opendap_url = opendap_url
        print('OpenDAP URL available.')

    def retrieve_data(self,vartime,var1,var2,var3,pointrange):  #Order: Time stream name, var1 stream name, var2 stream name, var3 stream name, rows to keep in arrays.
        prev_vartime = self.vartime
        prev_var1 = self.var1
        prev_var2 = self.var2
        prev_var3 = self.var3
       
        data = xr.open_dataset(self.opendap_url)
        vartime = data[vartime] 
        var1 = data[var1]                                
        var2 = data[var2] 
        var3 = data[var3]
        print('Data collected.')

        vartime = np.append(vartime,prev_vartime)
        var1 = np.append(var1,prev_var1)
        var2 = np.append(var2,prev_var2)
        var3 = np.append(var3,prev_var3)
        
        print('Data appended.')
        
        if vartime.shape[0] > pointrange:
            print('Trimming arrays.')
            vartime = vartime[-pointrange:]
            var1 = var1[-pointrange:]
            var2 = var2[-pointrange:]
            var3 = var3[-pointrange:]
        else: 
            print('No trimming required.')

        self.vartime = vartime
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3
        
    def plot_data(self,timename,var1name,var1units,var2name,var2units,var3name,var3units):  #Order, variable names and units.
        print('Plotting data.')
        plotvartime = np.array(self.vartime,dtype = 'datetime64')
        plotvartime = pd.to_datetime(plotvartime,format='%Y%m%d %H:%M:%S', errors='coerce',utc = True)
        plotvar1 = np.array(self.var1)
        plotvar2 = np.array(self.var2)
        plotvar3 = np.array(self.var3)

        ax1.clear()
        tplot = ax1.scatter(x=plotvartime,y=plotvar1,s=1,c=plotvar2,cmap='jet')
        fig.colorbar(tplot,ax=ax1, label = var2units)  #Assign the temperature plot a colorbar.
        ax1.invert_yaxis()  #Invert the y-axis of the plot so it makes sense.
        ax1.set_title(var2name)  #Title the plot.
        ax1.set_ylabel(var1name + ' (' + var1units+ ') ')  #Give the y axis a label.
        ax1.set_xlabel(timename)  #Give the x axis a label.
        ax1.xaxis.set_major_formatter(fmt) 
        ax1.tick_params(labelrotation=0)
        ax1.set_xlim(left = plotvartime[0],right = plotvartime[-1])

        ax2.clear()
        splot = ax2.scatter(x=plotvartime,y=plotvar1,s=1,c=plotvar3,cmap='jet')
        fig.colorbar(splot,ax=ax2,label = var3units)  #Assign the temperature plot a colorbar.
        ax2.invert_yaxis()  #Invert the y-axis of the plot so it makes sense.
        ax2.set_title(var3name)  #Title the plot.
        ax2.set_ylabel(var1name + ' (' + var1units+ ') ')   #Give the y axis a label.
        ax2.set_xlabel(timename)  #Give the x axis a label.
        ax2.xaxis.set_major_formatter(fmt) 
        ax2.tick_params(labelrotation=0)
        ax2.set_xlim(left = plotvartime[0],right = plotvartime[-1])

        ctrlfstr = 'Use CTRL + F to enter or exit fullscreen.'
        textbox = ax1.text(0.05,0.975,ctrlfstr,fontsize=8,transform = plt.gcf().transFigure,color = 'k')
                 
def animate(j): 
    print('Setting up request for loop({:2d}).'.format(j))
    OOI.create_url(interval,partial_url)
    OOI.request_data(user,token)
    OOI.retrieve_data(vartime,var1,var2,var3,pointrange)
    OOI.plot_data(timename,var1name,var1units,var2name,var2units,var3name,var3units)
    print('Next request for data in {:2d} hour(s).'.format(interval))

print('Setting up initial request.')      
root = tkinter.Tk()  #Create a Tk object to get the screen dimensions.
width = root.winfo_screenwidth()  #Define the screen width in pixels.
height = root.winfo_screenheight()  #Define the screen height in pixels
dpi = 100  #Define the number of pixes per inch.
fig = plt.figure(figsize=(width/dpi,height/dpi),facecolor = 'gray',edgecolor = 'black')  
ax1,ax2 = fig.subplots(2,1)  #Add subplots
fmt = mdates.DateFormatter('%m-%d %H:%M')  #Define how the dates are displayed.
plt.tight_layout(pad = pad)
fig.canvas.set_window_title(windowtitle)  #Set the window title.
fig.suptitle(windowtitle)  #Add a title for the figure.
root.destroy()  #Remove the Tk object because it is annoying.

OOI = OOI()
OOI.create_url(backcast,partial_url)
OOI.request_data(user,token)
OOI.retrieve_data(vartime,var1,var2,var3,pointrange)
OOI.plot_data(timename,var1name,var1units,var2name,var2units,var3name,var3units)
plt.draw()
print('Waiting for {:2d} hour(s) before initiating next request.'.format(interval))
plt.pause(interval * 60 * 60)
ani = animation.FuncAnimation(fig,animate,interval = interval * 60 * 60 * 1000)
plt.show()

