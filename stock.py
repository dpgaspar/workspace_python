import datetime as DT

import urllib
import pickle
from multiprocessing import Process



# --------------------------------
#  STOCK CELL
# --------------------------------
class StockCell():
    def __init__(self, ticker,date='20130101',popen=0.0,phigh=0.0,plow=0.0,pclose=0.0,pvol=0.0,adjclose=0.0):
        self.ticker = ticker
        self.date = DT.datetime.strptime(date, "%Y-%m-%d")
        self.O = float(popen)
        self.H = float(phigh)
        self.L = float(plow)
        self.C = float(pclose)
        self.V = float(pvol)
        self.adjclose = float(adjclose)
        # faz do adj close o close
        self.C = self.adjclose
        
    def set(self,date,popen,phigh,plow,pclose,pvol,adjclose=0): 
        self.date = DT.datetime.strptime(date, "%Y-%m-%d")
        self.O = popen
        self.H = phigh
        self.L = plow
        self.C = pclose
        self.V = pvol
        self.adjclose = adjclose
        
    def get(self):
        return {'date': self.date, 'open': self.O, 'high': self.H, 'low':self.L,'close':self.C,'vol':self.V,'adjclose':self.adjclose}
        
    def __str__(self):
        return "%s -> date:%s, open:%f, high:%f, low:%f, close:%f, Volume:%f, adjClose:%f" % (self.ticker, self.date,self.O,self.H,self.L,self.C,self.V,self.adjclose)    


# --------------------------------
#  STOCK LOADER
# --------------------------------
class StockLoader():
    def __init__(self, data_dir="./data"):
        self.data_dir = data_dir
    
    def download_historical_prices(self,symbol, start_date, end_date):
        url = 'http://ichart.yahoo.com/table.csv?s=%s&' % symbol + \
        'd=%s&' % str(int(end_date[4:6]) - 1) + \
        'e=%s&' % str(int(end_date[6:8])) + \
        'f=%s&' % str(int(end_date[0:4])) + \
        'g=d&' + \
        'a=%s&' % str(int(start_date[4:6]) - 1) + \
        'b=%s&' % str(int(start_date[6:8])) + \
        'c=%s&' % str(int(start_date[0:4])) + \
        'ignore=.csv'
        days = urllib.urlopen(url).readlines()
        if days[1].find("404 Not Found") != -1 :
            raise Exception("Ticker Not Found")
        download_data = ( [day[:-2].split(',') for day in days])
        download_data.pop(0)
        return download_data    
    
    def get_historical_prices(self,symbol, start_date, end_date):
        start_date_arg = start_date
        data = self.load_historical_prices(symbol)
        if (len(data) > 0):
            newest_date_from_file = DT.datetime.strptime(data[0][0], "%Y-%m-%d")
            oldest_date_from_file = DT.datetime.strptime(data[len(data)-1][0], "%Y-%m-%d")
            oldest_date_from_arg = DT.datetime.strptime(start_date, "%Y%m%d")            
            if (oldest_date_from_file <= oldest_date_from_arg):
                start_date = DT.datetime.strftime(newest_date_from_file,"%Y%m%d")
            if (oldest_date_from_arg < oldest_date_from_file):
                end_date = DT.datetime.strftime(oldest_date_from_file,"%Y%m%d")

        download_data = self.download_historical_prices(symbol, start_date, end_date)
        retdata = self.join_lists(download_data, data)
    
        # DEBUG
        #print "download:" , download_data[0][0], "->", download_data[len(download_data)-1][0]
        #if data != []: print "file:" , data[0][0], "->", data[len(data)-1][0]
        #print "retData:" , retdata[0][0], "->", retdata[len(retdata)-1][0]
     
        self.save_historical_prices(symbol, retdata)                
        return self.truncate_list(start_date_arg, retdata)

    def join_lists(self,l1, l2):
        l3 = []
        for e in l1:
            if e not in l2:
                l3.append(e)
        if (len(l3) > 0) and (len(l2) > 0):
            if (DT.datetime.strptime(l3[0][0], "%Y-%m-%d")) < (DT.datetime.strptime(l2[0][0], "%Y-%m-%d")):
                return l2 + l3
            else: 
                return l3 + l2
        else:
            if (len(l3) == 0): return l2
            else: return l1
    
    def truncate_list(self,start_date_arg, l1):
        start_date = DT.datetime.strptime(start_date_arg, "%Y%m%d")
        i = 0
        for cell in l1:
            cell_date = DT.datetime.strptime(cell[0], "%Y-%m-%d")
            if (start_date >= cell_date):
                return l1[0:i]
            i = i + 1
        return l1

    def save_historical_prices(self,symbol, data):
        filehandler = open(self.data_dir + "/" + symbol + ".dat", "wb")
        pickle.dump( data, filehandler)
        filehandler.close()
    
    def load_historical_prices(self, symbol):
        try:    
            filehandler = open(self.data_dir + "/" + symbol + ".dat", "rb")
            data = pickle.load( filehandler )
            filehandler.close()
            return data
        except: return []



# --------------------------------
#  STOCK DATA
# --------------------------------
class StockData(StockLoader):    
    def __init__(self, ticker="", data_dir="./data"):
        self.ticker = ticker
        self.history = []
        self.dates = []
        self.Os = []
        self.Hs = []
        self.Ls = []
        self.Cs = []
        self.Vs = []
        StockLoader.__init__(self, data_dir)
        
    def __eq__(self, other):
        if (self.ticker == other):
            return True
        else: 
            return False
    
    def D(self): return self.dates
    def O(self): return self.Os
    def H(self): return self.Hs
    def L(self): return self.Ls
    def C(self): return self.Cs
    def V(self): return self.Vs
    
    def load_file(self, ticker, startdate='19000101',enddate=DT.datetime.strftime(DT.datetime.today(),"%Y%m%d")):
        lst_data = self.load_historical_prices(ticker)
        lst_data = self.truncate_list(startdate, lst_data)
        lst_data.reverse()
        for cell in lst_data:
            s1 = StockCell(self.ticker,cell[0],cell[1],cell[2],cell[3],cell[4],cell[5],cell[6])
            self.history.append(s1)
            
            self.dates.append(DT.datetime.strptime(cell[0], "%Y-%m-%d"))
            self.Os.append(float(cell[1]))
            self.Hs.append(float(cell[2]))
            self.Ls.append(float(cell[3]))
            # faz do adj Close o Close
            self.Cs.append(float(cell[6]))            
            self.Vs.append(float(cell[5]))
        
    
    def load(self, ticker, startdate='19000101',enddate=DT.datetime.strftime(DT.datetime.today(),"%Y%m%d")):
        self.ticker = ticker
        self.history = []
        try:
            lstdata = StockLoader.get_historical_prices(self, self.ticker, startdate, enddate)
        except: return False
        lstdata.reverse()
        for cell in lstdata:
            s1 = StockCell(self.ticker,cell[0],cell[1],cell[2],cell[3],cell[4],cell[5],cell[6])
            self.history.append(s1)
            
            self.dates.append(DT.datetime.strptime(cell[0], "%Y-%m-%d"))
            self.Os.append(float(cell[1]))
            self.Hs.append(float(cell[2]))
            self.Ls.append(float(cell[3]))
            # faz do adj Close o Close
            self.Cs.append(float(cell[6]))            
            self.Vs.append(float(cell[5]))
        return True   
                                
    def __str__(self):
        strret = ""
        for s in self.history:
            strret = strret + str(s) + "\n"    
        return strret
    

# --------------------------------
#  STOCK DATA COL
# --------------------------------
class StockDataCollection():
    def __init__(self):
        self.stk_data_coll = []
        self.conf_file = ""
        self.startdate = ""
        self.conf_file = ""

    def load_th(self, ticker, stk_data, startdate, enddate):
        if stk_data.load(ticker, startdate, enddate):
            self.stk_data_coll.append(stk_data.ticker)
            print('.' + ticker)
        else: print "! not found ", ticker         
        
    
    def set_colection(self, conf_file="market.conf"):
        self.conf_file = conf_file
        f = open(conf_file, "rb")
        self.stk_data_coll = [x.strip() for x in f.readlines()]
        f.close()
        
    def load(self, conf_file="market.conf",startdate='19300101', paralel_count=10):
        self.stk_data_coll = []
        self.conf_file = conf_file
        self.startdate = startdate
        
        enddate_d = DT.datetime.today()
        enddate = DT.datetime.strftime(enddate_d,"%Y%m%d")
        f = open(conf_file, "rb")
        tickers = [x.strip() for x in f.readlines()]
        
        pp = 0
        
        p_lst = []
        for ticker in tickers:
            stk_data = StockData()                        
            p_lst.append(Process(target=self.load_th, args=(ticker, stk_data, startdate, enddate)))
            p_lst[len(p_lst) - 1].start()
            if (pp == paralel_count): 
                for i in range(0, len(p_lst)):
                    p_lst.pop().join()
                pp = 0
            else: pp = pp + 1
        for i in range(0, len(p_lst)):
            p_lst.pop().join()
        f.close()

    def get_tickers(self):
        return [x.ticker for x in self.stk_data_coll]

    def get_data(self, ticker):
        return  self.stk_data_coll[ self.stk_data_coll.index(ticker)]



# --------------------------------
#  STOCK FUNCTIONS
# --------------------------------
class StockCalc():
    def __init__(self):
        pass
    
    def sma(self, data, subset_size):
        retData = ([],[])
        divisor = float(subset_size)
        for x in range(subset_size, len(data[0]) + 1):
            retData[0].append(sum(data[0][x - subset_size:x]) / divisor)
            retData[1].append(data[1][x-1])
        return retData 
    
    def perc_diff(self,A,B):
        return ((B*100)/A)-100
    
    def perc_diffs(self, data):
        retData = ([],[])
        for x in range(1, len(data[0])):
            retData[0].append(self.perc_diff(data[0][x-1],data[0][x]))
            retData[1].append(data[1][x])
        return retData
    
    def volatility(self, data):
        data1 = self.perc_diffs(data)
        retData = ([],[])
        for x in range(1, len(data1[0])):
            retData[0].append(abs(data1[0][x]-data1[0][x-1]))
            retData[1].append(data[1][x])
        return retData
    
    # data = ([close],[volume],[date])
    def obv(self, data):
        retData = ([],[])
        for x in range(1, len(data[0])):
            if (data[0][x-1] < data[0][x]):
                if (x == 1):
                    retData[0].append(data[1][x-1])
                else: retData[0].append(retData[0][x-2] + data[1][x-1])
            else:
                if (x == 1):
                    retData[0].append(-data[1][x-1])
                else: retData[0].append(retData[0][x-2] - data[1][x-1])
            retData[1].append(data[2][x])
        return retData        

    def llv(self, data, period):
        retData = ([],[])
        retData[0].append(data[0][0])
        retData[1].append(data[1][0])
        per = 0
        for x in range(1, len(data[0])-2):
            if (retData[0][x-1] > data[0][x]):
                retData[0].append( data[0][x])
                per = 0
            else:
                if (per == period):
                    retData[0].append( data[0][x])
                    per = 0
                else:
                    retData[0].append(retData[0][x-1])
                    per = per + 1
            retData[1].append(data[1][x])
        return retData    
            
class StockCalcIndex(StockCalc):
    def __init__(self, stk_data_coll):
        self.stk_data_coll = stk_data_coll
        StockCalc.__init__(self)
        
    
    def init_list(self, data):        
        retData = ([],[])
        for i in range(0,len(data[1])-1):
            retData[0].append(0.0)
            retData[1].append(data[1][i])
        return retData
    
    def correlation(self, data):
        retData = self.init_list(data)
        
        for c in self.stk_data_coll.stk_data_coll:
            print c
            sd = StockData()
            sd.load_file(c)
            for x in range(0,len(data[1])-1):
                date = data[1][x]
                #print date        
                try:
                    j = sd.dates.index(date)
                    if (sd != 0):
                        if (sd.Cs[j-1] > sd.Cs[j]) and (data[0][x-1] > data[0][x]):
                            retData[0][x] = retData[0][x] + 1.0
                        elif (sd.Cs[j-1] < sd.Cs[j]) and (data[0][x-1] < data[0][x]): 
                            retData[0][x] = retData[0][x] + 1.0
                        else: retData[0][x] = retData[0][x] - 1.0
                except: pass
        return retData
        
    def correlation_adj(self, data):
        retData = self.init_list(data)
            
        for c in self.stk_data_coll.stk_data_coll:
            print c
            sd = StockData()
            sd.load_file(c)
            for x in range(0,len(data[1])-1):
                date = data[1][x]
                #print date        
                try:
                    j = sd.dates.index(date)
                    if (sd != 0):
                        if (sd.Cs[j-1] > sd.Cs[j]) and (data[0][x-1] > data[0][x]):
                            retData[0][x] = retData[0][x] + 1.0
                        elif (sd.Cs[j-1] < sd.Cs[j]) and (data[0][x-1] < data[0][x]): 
                            retData[0][x] = retData[0][x] + 1.0
                        else: 
                            retData[0][x] = retData[0][x] - 1.0
                except:
                    retData[0][x] = retData[0][x] - 1.0
        return retData
            

        