import stock as stk
import portfolio as portf
import plot
import sys
import cmd
import os
import decision as des
   
   
class CLI(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = '$> '
        self.stk_data_coll = stk.StockDataCollection()
        self.add_to_plot_lst = []
        self.paralel_count = 10
    
    def do_set_paralel_count(self, arg):
        self.paralel_count = arg
        
    def do_get_paralel_count(self, arg):
        print self.paralel_count
        
    def help_set_paralel_count(self):
        print "syntax: set_paralel_count [NUMBER]",
        print "-- update self.paralel_count for load command"
 
    
    def do_load_collection(self, arg):
        self.stk_data_coll.load(conf_file=arg, paralel_count=self.paralel_count)
        print "---------------------------------------"
        print "Data downloaded for ", arg 
        
    def help_load_collection(self):
        print "syntax: load [portfolio file]",
        print "-- load/updates the tickers from portfolio file"

    def do_set_collection(self, arg):
        self.stk_data_coll.set_colection(arg)
        
    def help_set_collection(self):
        print "syntax: set_collection [portfolio file]",
        print "-- set the tickers from portfolio file"

    
    def do_get_collection(self, arg):
        print "-----------------------------"
        print " Collection from ", self.stk_data_coll.conf_file
        print "-----------------------------"
        for c in self.stk_data_coll.stk_data_coll:
            print c
            
 
    def do_cleanup(self, arg):
        filelist = [ f for f in os.listdir(".") if f.endswith(".dat") ]
        for f in filelist:
            os.remove(f)
 
    def help_cleanup(self):
        print "syntax: cleanup",
        print "-- removes all data files"
 

    def do_plot_indexes(self, arg):   
        indexes = arg.split(',',1)
        a_plot = plot.Plot(plot.PlotCellIndex(indexes[0]))
        try:
            for index in indexes[1:]:
                p = plot.PlotCellIndex(index)
                a_plot.addSimple(plot.PlotCell((p.data,p.dates)))
        finally: a_plot.plot()
        
    def help_plot_indexes(self):
        print "syntax: plot_index [index_name1,index_name2,....]",
        print "-- plot slimple index from csv"
        
    def do_plot_ticker_indexes(self,arg):
        calc = stk.StockCalcIndex(self.stk_data_coll)
        sd = stk.StockData()
        ticker, indexes, startdate = arg.split()
        indexes = indexes.split(',',1)
        
        sd.load(ticker, startdate)
        a_plot = plot.Plot(plot.PlotCell((sd.Cs,sd.dates)))
        
        a_plot.addSimple(plot.PlotCell( calc.sma((sd.Cs, sd.dates), 200),overlay=True))
        a_plot.addSimple(plot.PlotCell( calc.sma((sd.Cs, sd.dates), 50),overlay=True))
        
        for index in indexes:
            p = plot.PlotCellIndex(index)
            p.truncate(startdate)
            a_plot.addSimple(plot.PlotCell((p.data,p.dates)))        
            a_plot.addSimple(plot.PlotCell(calc.sma((p.data,p.dates),10)))
            a_plot.addSimple(plot.PlotCell(calc.sma((p.data,p.dates),50),overlay=True))
        
        a_plot.plot()
        
    def do_plot_collection(self, arg):
        calc = stk.StockCalcIndex(self.stk_data_coll)
        sd = stk.StockData()
        ticker, startdate = arg.split()
        
        sd.load(ticker, startdate)
        a_plot = plot.Plot(plot.PlotCell((sd.Cs,sd.dates)))
        
        a_plot.addSimple(plot.PlotCell( calc.sma((sd.Cs, sd.dates), 200),overlay=True))
        a_plot.addSimple(plot.PlotCell( calc.sma((sd.Cs, sd.dates), 50),overlay=True))
        a_plot.addSimple(plot.PlotCell( calc.llv((sd.Cs, sd.dates), 100),overlay=True))

        a_plot.addSimple(plot.PlotCell( calc.sma((sd.Vs,sd.dates),20 )))
        a_plot.addSimple(plot.PlotCell( calc.obv((sd.Cs,sd.Vs,sd.dates) )))
        
        a_plot.addSimple(plot.PlotCell( calc.correlation_adj((sd.Cs,sd.dates))))
                
        a_plot.plot()


    def do_plot(self, arg):
        calc = stk.StockCalcIndex(self.stk_data_coll)
        sd = stk.StockData()
        ticker, startdate = arg.split()
        
        sd.load(ticker, startdate)
        a_plot = plot.Plot(plot.PlotCell((sd.Cs,sd.dates)))
        
        a_plot.addSimple(plot.PlotCell( calc.sma((sd.Cs, sd.dates), 200),overlay=True))
        a_plot.addSimple(plot.PlotCell( calc.sma((sd.Cs, sd.dates), 50),overlay=True))
        a_plot.addSimple(plot.PlotCell( calc.llv((sd.Cs, sd.dates), 100),overlay=True))

        a_plot.addSimple(plot.PlotCell( calc.sma((sd.Vs,sd.dates),20 )))
        a_plot.addSimple(plot.PlotCell( calc.obv((sd.Cs,sd.Vs,sd.dates) )))        
        
        a_plot.plot()

        
    def help_plot(self):
        print "syntax: plot [ticker] []|[start date YYYYMMDD]",
        print "-- plots the ticker"
 
    
    def do_simulation(self, arg):
        ticker, startdate = arg.split()
        sd = stk.StockData()
        calc = stk.StockCalc()
        sd.load(ticker, startdate)
        
        port = portf.PortfolioSimulator()
        port.add_indicator( calc.sma((sd.Cs, sd.dates), 50))
        port.add_indicator( calc.sma((sd.Cs, sd.dates), 200))
                        
        port.run(sd.history)
        port.print_short_log()
    
    def do_simulation2(self, arg):
        ticker, startdate = arg.split()
        sd = stk.StockData()
        sd.load(ticker, startdate)
                
        port = des.DecisionCollection(ticker, 10000)
        decision = des.DecisionSimpleSMA(ticker, (sd.Cs, sd.dates), port)
        decision.looper()
        print ticker, ":", str(port)
    
    
    
    def help_simulation(self):
        print "syntax: simulation [ticker] []|[start date YYYYMMDD]",
        print "-- runs a simulation on a single ticker"
    
    
    
        
    def do_simulation_collection(self, arg ):
        
        for ticker in self.stk_data_coll.stk_data_coll:
            sd = stk.StockData()
            sd.load_file(ticker, arg)
            calc = stk.StockCalc()
            
            port = portf.PortfolioSimulator()
            port.add_indicator( calc.sma((sd.Cs, sd.dates), 50))
            port.add_indicator( calc.sma((sd.Cs, sd.dates), 200))
            
            port.run(sd.history)
            print ticker + ":" + str(port)
        
    
         
    def emptyline(self):
        pass
 
    def do_quit(self, arg):
        sys.exit(1)
 
if __name__ == "__main__": 
     
     cli = CLI()
     cli.cmdloop()
     