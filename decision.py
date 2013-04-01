import stock as stk

class DecisionLogEntry():
    def __init__(self, decision_type, poscell, total_value):
        self.decision_type = decision_type
        self.poscell = poscell
        self.total_value = total_value
        
    def __str__(self):
        return "%s:%s: %f %d Quantity=%d" % (self.decision_type, self.poscell.name, self.poscell.value, self.poscell.date, self.quantity)

class PositionCell():
    def __init__(self, name, value, date, quantity):
        self.name = name
        self.value = value
        self.date = date
        self.quantity = quantity
        
    def __eq__(self, other):
        if other == self.name: return True
        return False
    
    def __ne__(self, other):
        if other != self.name: return True
        return False
    
    def __str__(self): return self.name + " V=" + str(self.value) + " D=" + str(self.date) + " Q=" + str(self.quantity)

class DecisionCollection():
    def __init__(self, name, init_value):
        self.init_value = init_value
        self.curr_value = init_value
        self.name = name
        self.positions = []
        self.decision_log = []
        
    def enter(self, name, value, date, quantity):
        if quantity == -1: quantity = self.get_max_quantity(value)
        if value*quantity < self.curr_value:
            if name in self.positions:
                position = self.positions[self.positions.index(name)]
                position.value = (position.value*position.quantity) + (value*quantity)/(position.quantity + quantity) 
                position.quantity = position.quantity + quantity
            else:
                self.positions.append(PositionCell(name, value, date, quantity))
            self.curr_value = self.curr_value - (value*quantity)
            self.decision_log.append(DecisionLogEntry("ENTER", PositionCell(name, value, date, quantity), self.get_total_value()))
            return True
        return False
        
    def leave(self, name, value, date, quantity):
        if name in self.positions:
            position = self.positions[self.positions.index(name)]
            if (position.quantity == quantity) or (quantity == -1):
                quantity = position.quantity 
                self.positions.pop(self.positions.index(name))
            else:
                position.value = (position.value*position.quantity) - (value*quantity)/(position.quantity - quantity) 
                position.quantity = position.quantity - quantity
            self.curr_value = self.curr_value + (value*quantity)
            self.decision_log.append(DecisionLogEntry("LEAVE", PositionCell(name, value, date, quantity), self.get_total_value()))            
            return True
        else: return False
        
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
    
        
        
class DecisionCell():
    def __init__(self, decision=False, quantity=0):
        self.answer = decision
        self.quantity = quantity

class Decision():
    # target_data = ([Vs][Dates])
    def __init__(self, target_name, target_data, decision_col):
        self.calc = stk.StockCalc()
        self.indicators = []
        self.stop_indicator = ([],[])
        self.target_name = target_name
        self.target_data = target_data
        self.decision_col = decision_col
        self.__init_indicators__()
                
    def __init_indicators__(self):
        pass
    
    def enter_decision(self, i):
        pass
    
    def leave_decision(self, i):
        pass
    
    def get_value(self, i): return self.target_data[0][i]
    
    def get_date(self, i): return self.target_data[1][i]
    
    def get_indicator_for_date(self, date):
        retlst = []
        for ind in self.indicators:
            try: 
                v = ind[1].index(date)
                retlst.append(ind[0][v])
            except: return []
        return retlst
    
    def looper(self):
        on = False
        for i in range(0, len(self.target_data[0])-1):
            d = self.target_data[1][i]
            col_indicator = self.get_indicator_for_date(d)
            if len(col_indicator) > 0:
                if not on:
                    decision = self.enter_decision(i, col_indicator)
                    if (decision.answer):
                        self.decision_col.enter(self.target_name, self.get_value(i), self.get_date(i), decision.quantity)
                        on = True
                if on:
                    decision = self.leave_decision(i, col_indicator)
                    if (decision.answer):
                        self.decision_col.leave(self.target_name, self.get_value(i), self.get_date(i), decision.quantity)
                        on = False        
                
                                                        
   
class DecisionSimpleSMA(Decision):
    def __init__(self, target_name, target_data, decision_col):
        Decision.__init__(self, target_name, target_data, decision_col)
        
    def __init_indicators__(self):
        Decision.__init_indicators__(self)        
        self.indicators.append(self.calc.sma((self.target_data[0], self.target_data[1]), 50))
        self.indicators.append(self.calc.sma((self.target_data[0], self.target_data[1]), 200))
        self.stop_indicator = (self.calc.llv((self.target_data[0], self.target_data[1]), 40))
        
    def enter_decision(self, i, col_indicator):
        Decision.enter_decision(self, i)
        return DecisionCell(col_indicator[0] > col_indicator[1], -1)
        
    def leave_decision(self, i, col_indicator):
        Decision.leave_decision(self, i)
        return DecisionCell(col_indicator[0] < col_indicator[1], -1)
        
    