import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import datetime as DT

import pickle
import csv



# --------------------------------
#  PLOT CELL
# --------------------------------
class PlotCell():
    # INIT com data em Tuple(Data,Dates)
    def __init__(self, data, overlay=False, color='-'):
        self.data = data[0]
        self.dates = data[1]
        self.overlay=overlay
        self.color = color

class PlotCellIndex(PlotCell):
    def __init__(self, index_name,overlay=False, color='-'):
        self.data_dir = "./data"
        data = self.load_file(index_name)
        PlotCell.__init__(self, data, overlay, color)
    
    def truncate(self, startdate):
        start_date = DT.datetime.strptime(startdate, "%Y%m%d")
        for x in range(0,len( self.dates)-1):
            if (self.dates[x] > start_date):
                break
        self.data = self.data[x:]
        self.dates = self.dates[x:]
        
    def load_file(self, index_name):
        try:    
            filehandler = open(self.data_dir + "/" + index_name + ".idx", "rb")
            data = pickle.load( filehandler )
            filehandler.close()
            return data
        
        except:
            data = ([],[])
            try:
                
                csv_file = self.data_dir + "/" + index_name + ".csv" 
                with open(csv_file, 'rb') as csvfile:
                    dialect = csv.Sniffer().sniff(csvfile.read(1024))
                    csvfile.seek(0)
                    data_lines = csv.reader(csvfile, dialect)
                    for row in data_lines:
                        data[0].append(float(row[0]))
                        try:
                            data[1].append(DT.datetime.strptime(row[1], "%Y-%m-%d"))
                        except:
                            try: 
                                data[1].append(DT.datetime.strptime(row[1], "%Y/%m/%d"))
                            except: data[1].append(DT.datetime.strptime(row[1], "%Y%m%d"))                        
                return data
            except Exception as e:
                print "NOP", e
                return data

             

# --------------------------------
#  PLOT
# --------------------------------
class Plot():
    
    full_rect_x = 0.05
    full_rect_y = 0.1
    full_rect_width = 0.95
    full_rect_height = 0.9
    
    
    def __init__(self, plotcell, firstRatio=1.7):
        plt.rc('axes', grid=True)
        plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
        self.figure1 = plt.figure()
        self.plotcell_lst = []
        self.plotRects = []
        self.firstRatio = firstRatio
        self.plotcell_lst.append(plotcell)
        rect1 = [self.full_rect_x,self.full_rect_y , self.full_rect_width, self.full_rect_height]
        self.plotRects.append(rect1)
    
    
    def addSimple(self,plotcell):
        
        self.plotcell_lst.append(plotcell)
        if not plotcell.overlay:
            self.plotRects.append([self.full_rect_x,0,self.full_rect_width,0])
            n = len(self.plotRects)
            i = 0
            height = (self.full_rect_height)/n
            highHeight = height*self.firstRatio
            lowHeight = (self.full_rect_height-highHeight)/(n-1)
                     
            for rect in reversed(self.plotRects):
                if (i == len(self.plotRects)-1): 
                    rect[1] = (lowHeight*i)+self.full_rect_y              
                    rect[3] = highHeight
                else: 
                    rect[1] = (lowHeight*i)+self.full_rect_y              
                    rect[3] = lowHeight
                i = i + 1
    
    
    def plot(self):
        ax_list = []
        i = 0
        for p_cell in self.plotcell_lst:
            p_data = p_cell.data
            p_dates = p_cell.dates
            p_color = p_cell.color
            if (i == 0):  ax_list.append(self.figure1.add_axes(self.plotRects[i]) )
            else:
                if not p_cell.overlay:
                    ax_list.append(self.figure1.add_axes(self.plotRects[i], sharex=ax_list[0]) )
                else: i = i - 1
            
            ax_list[i].plot(p_dates,p_data,p_color)
            i = i + 1
                
        for label in ax_list[len(ax_list)-1].get_xticklabels():
            label.set_rotation(30)            
            label.set_horizontalalignment('right')
        
        for x in ax_list: Cursor(x , useblit=True, color='red', linewidth=1 )
                         
        plt.Artist()
        plt.show()
        
