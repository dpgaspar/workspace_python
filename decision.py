import stock as stk
 


#-------------------------------------
# Decision Log Entry
#
# Estrutura de Celula de dados
# guarda um log das decisoes
#-------------------------------------
class DecisionLogEntry():
    def __init__(self, decision_type, poscell, total_value, ptr_poscell=None):
        self.decision_type = decision_type
        self.poscell = poscell
        self.total_value = total_value
        self.ptr_poscell = ptr_poscell
        
    def __str__(self):
        return "%s:%s: %f %d Quantity=%d" % (self.decision_type, self.poscell.name, self.poscell.value, self.poscell.date, self.quantity)

#-------------------------------------
# Position Cell
#
# Estrutura de Celula de dados
#-------------------------------------
class PositionCell():
    def __init__(self, name, value, date, quantity, stop_value=0.0):
        self.name = name
        self.value = value
        self.date = date
        self.quantity = quantity
        self.stop_value = stop_value
       
    def __eq__(self, other):
        if other == self.name: return True
        return False
    
    def __ne__(self, other):
        if other != self.name: return True
        return False
    
    def __str__(self): return self.name + " V=" + str(self.value) + " D=" + str(self.date) + " Q=" + str(self.quantity)


#-------------------------------------
# Decision Collection
#
# Objecto tipo portfolio
#-------------------------------------
class DecisionCollection():
    def __init__(self, name, init_value):
        self.init_value = init_value
        self.curr_value = init_value
        self.name = name
        self.positions = []
        self.decision_log = []
        
    def enter(self, name, value, date, quantity, stop_value=0.0):
        if quantity == -1: quantity = self.get_max_quantity(value)
        if value*quantity <= self.curr_value:
            if name in self.positions:
                position = self.positions[self.positions.index(name)]
                position.value = (position.value*position.quantity) + (value*quantity)/(position.quantity + quantity)
                position.quantity = position.quantity + quantity
            else:
                self.positions.append(PositionCell(name, value, date, quantity, stop_value))
            self.curr_value = self.curr_value - (value*quantity)
            self.decision_log.append(DecisionLogEntry("ENTER", PositionCell(name, value, date, quantity, stop_value), self.get_total_value()))
            return True
        return False
        
    def leave(self, name, value, date, quantity, stop_value=0.0):
        if name in self.positions:
            position = self.positions[self.positions.index(name)]
            if (position.quantity == quantity) or (quantity == -1):
                quantity = position.quantity
                i = self.positions.index(name)
                buy_date = self.positions[i].date
                self.positions.pop(i)
            else:
                position.value = (position.value*position.quantity) - (value*quantity)/(position.quantity - quantity)
                position.quantity = position.quantity - quantity
            self.curr_value = self.curr_value + (value*quantity)
            self.decision_log.append(DecisionLogEntry("LEAVE", PositionCell(name, value, date, quantity, stop_value), self.get_total_value()))
            return True
        else: return False

    def get_stop_from_name(self, name):
        try:
            position = self.positions[self.positions.index(name)]
            return position.stop_value
        except:
            print self.positions
        
    def get_max_quantity(self, value):
        quantity = round(self.curr_value / value,0)
        if (quantity*value > self.curr_value): quantity = quantity -1
        return quantity
        
    def get_value(self):
        cvalue = 0.0
        for s in self.positions:
            cvalue = cvalue + s.value * s.quantity
        return cvalue
    
    def get_total_value(self):
        return self.curr_value + self.get_value()
    
    def get_years(self):
        return ((self.decision_log[len(self.decision_log)-1].poscell.date - self.decision_log[0].poscell.date).days/365)
    
    def get_year_rate(self):
        years = self.get_years()
        if years != 0:
            return ((((self.get_total_value())*100)/self.init_value)-100)/years
        else: return 0
    
    def __str__(self):
        retstr = "CASH=%f VALUE=%f TOTAL=%f " % (self.curr_value, self.get_value(), self.get_total_value())
        retstr = retstr + "TOTAL_TRANS=%d " % len(self.decision_log)
        if len(self.decision_log)>0:
            retstr = retstr + "YEAR_RATE=%f YEARS=%s " % (self.get_year_rate(),self.get_years())
        return retstr


class DecisionCollectionStat():
    def __init__(self):
        self.decision_lst = []
        
    def add(self, decision):
        self.decision_lst.append(decision_vol)
        
    def print_all(self):
        for cell in self.decision_lst:
            print cell.decision_col

    def load_sd_col(self, data_col_tickers, decision, startdate):
        for ticker in data_col_tickers:
            sd = stk.StockData()
            sd.load(ticker, startdate)
            des = copy.deepcopy(decision)
            des_col = DecisionCollection("PORTF", 10000)
            des.decision.post_set(sd, des_col)
            self.decision_lst.append(des)
     
    def loop_all():
         for cell in self.decision_lst:
            cell.looper()
               
        

#-------------------------------------
# Decision Cell
#
# Classe tipo celula de dados
#-------------------------------------
class DecisionCell():
    def __init__(self, decision=False, quantity=0, stop_value=0.0):
        self.answer = decision
        self.quantity = quantity
        self.stop_value = stop_value
        
#-------------------------------------
# Decision
#
# Classe tipo Interface
#-------------------------------------
class Decision():
    # target_data = ([Vs][Dates])
    def __init__(self, target_name, target_data=([],[]), decision_col=None, risk_factor=1):
        self.calc = stk.StockCalc()
        self.indicators = []
        self.stop_indicator = ([],[])
        self.target_name = target_name
        self.target_data = target_data
        self.decision_col = decision_col
        self.risk_factor = risk_factor
        self.__init_indicators__()
        self.indicators_index = [0] * len(self.indicators)
        
                
    def __init_indicators__(self):
        pass
    
    def post_set(self, sd, decision_col):
        self.target_data = (sd.Cs, sd.dates)
        self.decision_col = decision_col
    
    def enter_decision(self, i):
        pass
    
    def leave_decision(self, i):
        pass
    
    
    def get_quantity_from_stop(self, value, stop_value):
        if (value == stop_value):
            quantity = round(self.decision_col.curr_value / value,0)
            if (quantity*value > self.decision_col.curr_value): quantity = quantity -1
            return quantity
        else:
            quantity = (round(((self.decision_col.curr_value * self.risk_factor)/(value-stop_value)),0))
            if (quantity*value > self.decision_col.curr_value):
                quantity = round(self.decision_col.curr_value / value,0)
                if (quantity*value > self.decision_col.curr_value): quantity = quantity -1
            return quantity
    
    def get_value(self, i): return self.target_data[0][i]
    
    def get_date(self, i): return self.target_data[1][i]
    
    def get_stop_for_date(self, date):
        try:
            v = self.stop_indicator[0][self.stop_indicator[1].index(date)]
            return v
        except: return 0.0
    
    def get_indicator_for_date(self, date):
        retlst = []
        for i in range(0, len(self.indicators)):
            try:
                v = self.indicators[i][1].index(date, self.indicators_index[i])
                retlst.append(self.indicators[i][0][v])
                self.indicators_index[i] = v
            except:
                self.indicators_index[i] = 0 
                return []
        return retlst
    
    def looper(self):
        on = False
        for i in range(0, len(self.target_data[0])-1):
            if not on:
                decision = self.enter_decision(i)
                if (decision.answer):
                    if (self.decision_col.enter(self.target_name, self.get_value(i), self.get_date(i), decision.quantity, decision.stop_value)):
                        on = True                
            if on:
                if (self.get_value(i) < self.decision_col.get_stop_from_name(self.target_name)):
                    self.decision_col.leave(self.target_name, self.get_value(i), self.get_date(i), -1)
                    on = False
                else:
                    decision = self.leave_decision(i)
                    if (decision.answer):
                        self.decision_col.leave(self.target_name, self.get_value(i), self.get_date(i), decision.quantity, decision.stop_value)
                        on = False
                
                                                        
#-------------------------------------
# Decision Simple SMA
#
# Implementacao do Decision
#-------------------------------------
class DecisionSimpleSMA(Decision):
    def __init__(self, target_name, target_data=([],[]), decision_col=None, sma_fast=50, sma_slow=200, stop_per=40):
        self.sma_fast = sma_fast
        self.sma_slow = sma_slow
        self.stop_per = stop_per
        self.col_flag = True
        Decision.__init__(self, target_name, target_data, decision_col)
        
    def __init_indicators__(self):
        Decision.__init_indicators__(self)
        self.indicators.append(self.calc.sma((self.target_data[0], self.target_data[1]), self.sma_fast))
        self.indicators.append(self.calc.sma((self.target_data[0], self.target_data[1]), self.sma_slow))
         
    def enter_decision(self, i):
        Decision.enter_decision(self, i)
        d = self.get_date(i)
        col_indicator = self.get_indicator_for_date(d) 
        if (len(col_indicator) == len(self.indicators)):                        
            ac_col_flag = (col_indicator[0] > col_indicator[1])
            decision = DecisionCell(ac_col_flag and (not self.col_flag), -1)
            self.col_flag = ac_col_flag            
            return decision
        else:
            return DecisionCell(False, 0, 0) 
       
    def leave_decision(self, i):
        Decision.leave_decision(self, i)
        d = self.get_date(i)
        col_indicator = self.get_indicator_for_date(d)
        if (len(col_indicator) == len(self.indicators)):            
            ac_col_flag = (col_indicator[0] > col_indicator[1])
            decision = DecisionCell((not ac_col_flag) and self.col_flag, -1)
            self.col_flag = ac_col_flag
            return decision            
        else:
            return DecisionCell(False, 0, 0)
        
#-------------------------------------
# Decision Simple Stop SMA
#
# Implementacao do Decision
#-------------------------------------
class DecisionSimpleStopSMA(Decision):
    def __init__(self, target_name, target_data, decision_col, risk_factor=1, sma_fast=50, sma_slow=200, stop_per=40):
        self.sma_fast = sma_fast
        self.sma_slow = sma_slow
        self.stop_per = stop_per
        self.col_flag = True
        Decision.__init__(self, target_name, target_data, decision_col, risk_factor)
        
    def __init_indicators__(self):
        Decision.__init_indicators__(self)
        self.indicators.append(self.calc.sma((self.target_data[0], self.target_data[1]), self.sma_fast))
        self.indicators.append(self.calc.sma((self.target_data[0], self.target_data[1]), self.sma_slow))
        self.stop_indicator = (self.calc.llv((self.target_data[0], self.target_data[1]), self.stop_per))
        
    def enter_decision(self, i):
        Decision.enter_decision(self, i)        
        d = self.get_date(i)
        col_indicator = self.get_indicator_for_date(d)
        if (len(col_indicator) == len(self.indicators)):
            ac_col_flag = (col_indicator[0] > col_indicator[1])
            stop_value = self.get_stop_for_date(d)
            decision = DecisionCell(ac_col_flag and (not self.col_flag), self.get_quantity_from_stop(self.get_value(i), stop_value), stop_value)        
            self.col_flag = ac_col_flag
            return decision 
        else:
            return DecisionCell(False, 0, 0)
    def leave_decision(self, i):
        Decision.leave_decision(self, i)
        d = self.get_date(i)
        col_indicator = self.get_indicator_for_date(d)        
        if (len(col_indicator) == len(self.indicators)):        
            ac_col_flag = (col_indicator[0] > col_indicator[1])
            decision = DecisionCell(col_indicator[0] < col_indicator[1], -1)
            self.col_flag = ac_col_flag
            return decision
        else:
            return DecisionCell(False, 0, 0)
        