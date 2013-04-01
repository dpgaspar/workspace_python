import stock as stk



# --------------------------------
#  STOCK POSITION
# --------------------------------
class StockPosition(object):
    def __init__(self, stk_cell, quantity):
        self.stk_cell = stk_cell
        self.quantity = quantity

    def __eq__(self, other):
        if (self.stk_cell.ticker == other.ticker):
            return True
        else: 
            return False
        
    def __ne__(self, other):
        if (self.stk_cell.ticker != other.ticker):
            return True
        else: return False
        
# --------------------------------
#  ORDER LOG ENTRY
# --------------------------------
class OrderLogEntry():
    def __init__(self, order_type, stk_cell, quantity, total_value):
        self.order_type = order_type
        self.stk_cell = stk_cell
        self.quantity = quantity
        self.total_value = total_value
        
    def __str__(self):
        return "%s: %s Quantity=%d" % (self.order_type,self.stk_cell,self.quantity)


# --------------------------------
#  PORTFOLIO
# --------------------------------
class Portfolio():
    def __init__(self, name, cash):
        self.name = name
        self.cash = cash
        self.init_cash = cash
        self.stk_positions = []
        self.order_log = []
    
        
    def buy(self, stk_cell, quantity):
        if (stk_cell.C*quantity) > self.cash:
            print "NOT ENOUGH CASH QUANT=%f CASH=%d CLOSE=%f" % (quantity,self.cash,stk_cell.C)
            return False
        else:
            self.cash = self.cash - (stk_cell.C*quantity)
            self.stk_positions.append(StockPosition(stk_cell,quantity))
            self.order_log.append(OrderLogEntry("BUY",stk_cell,quantity, self.get_total_value()))
            return True
        
        
    def sell(self, stk_cell, quantity):
        i = self.stk_positions.index(stk_cell, )
        if (self.stk_positions[i].quantity == quantity):
            self.cash = self.cash + (stk_cell.C*quantity)
            self.stk_positions.pop(i)            
        else:
            self.cash = self.cash + (stk_cell.C*quantity)
            self.stk_positions[i].quantity = self.stk_positions[i].quantity - quantity             
        self.order_log.append(OrderLogEntry("SELL",stk_cell,quantity,self.get_total_value()))
    
    def buy_max(self,stk_cell):
        quantity = round(self.cash / stk_cell.C,0)
        if (quantity*stk_cell.C > self.cash): quantity = quantity -1   
        self.buy(stk_cell, quantity)
    
    def sell_max(self,stk_cell):
        i = self.stk_positions.index(stk_cell )
        self.sell(stk_cell,self.stk_positions[i].quantity)
    
    def get_value(self):
        cvalue = 0.0
        for s in self.stk_positions:
            cvalue = cvalue + s.stk_cell.C * s.quantity
        return cvalue
    
    def get_cash(self): return self.cash
    
    def get_total_value(self):
        return self.cash + self.get_value()
    
    def get_years(self):
        return ((self.order_log[len(self.order_log)-1].stk_cell.date - self.order_log[0].stk_cell.date).days/365)
    
    def get_year_rate(self):
        years = self.get_years()
        if years != 0:
            return ((((self.get_total_value())*100)/self.init_cash)-100)/years
        else: return 0    
    
    def print_long_log(self):
        for l in self.order_log:
            print l        
        print "------------------------------"            
        print "CASH=%f VALUE=%f TOTAL=%f" % (self.cash,self.get_value(),self.get_total_value())
        print "TOTAL TRANS %d" % len(self.order_log)
        years = ((self.order_log[len(self.order_log)-1].stk_cell.date - self.order_log[0].stk_cell.date).days/365)
        print "YEAR RATE=%f  ,for %s YEARS " % (((((self.get_total_value())*100)/self.init_cash)-100)/years, years)
 
    def print_short_log(self):
        print "------------------------------"            
        print "CASH=%f VALUE=%f TOTAL=%f" % (self.cash,self.get_value(),self.get_total_value()),
        print "TOTAL TRANS=%d" % len(self.order_log),
        if len(self.order_log)>0:
            years = ((self.order_log[len(self.order_log)-1].stk_cell.date - self.order_log[0].stk_cell.date).days/365)
            print "YEAR RATE=%f  ,for %s YEARS " % (((((self.get_total_value())*100)/self.init_cash)-100)/years, years)
 
    def __str__(self):

        retstr = "CASH=%f VALUE=%f TOTAL=%f " % (self.cash,self.get_value(),self.get_total_value())
        retstr = retstr + "TOTAL_TRANS=%d " % len(self.order_log) 
        if len(self.order_log)>0:
            retstr = retstr + "YEAR_RATE=%f YEARS=%s " % (self.get_year_rate(),self.get_years())          
        return retstr
# --------------------------------
#  AT
# --------------------------------
class PortfolioSimulator(Portfolio):
    def __init__(self, name="Teste", cash=10000):
        self.indicators = []
        self.stop_indicator = ([],[])
        Portfolio.__init__(self, name, cash)
        
    
    def add_indicator(self, data):
        self.indicators.append(data)
    
    def get_buy_plot_cell(self):
        pc = ([],[])
        for p in self.order_log:
            if p.order_type == "BUY":
                pc[0].append(p.stk_cell.C)
                pc[1].append(p.stk_cell.date)
        return pc
    
    def get_sell_plot_cell(self):
        pc = ([],[])
        for p in self.order_log:
            if p.order_type == "SELL":
                pc[0].append(p.stk_cell.C)
                pc[1].append(p.stk_cell.date)
        return pc
    
    def get_total_value_plot_cell(self):
        pc = ([],[])
        for p in self.order_log:
            pc[0].append(p.total_value)
            pc[1].append(p.stk_cell.date)
        return pc
    
    def run(self, stk_data):
        i = 0
        j = 0
        k = 0
        b_flag = False
        for p in stk_data:
            #print p,self.indicators[0][1][j]
            if (p.date == self.indicators[0][1][j]):
                if (p.date == self.indicators[1][1][k]):
                    if (self.indicators[0][0][j] > self.indicators[1][0][k]) and not b_flag:
                        self.buy_max(p)
                        b_flag = True
                    elif (self.indicators[0][0][j] < self.indicators[1][0][k]) and b_flag:
                        self.sell_max(p)
                        b_flag = False
                    k = k + 1
                j = j + 1
            i = i + 1
    