import stock as stk
import portfolio as portf
import sys
    
    
if __name__ == "__main__":   
    a = stk.StockData()
    a.load(sys.argv[1],sys.argv[2],sys.argv[3])
   
    calc = stk.StockCalc()
    
    at = portf.AT(a.history, 10000)
    at.add_indicator( calc.sma((a.Cs, a.dates), 50))
    at.add_indicator( calc.sma((a.Cs, a.dates), 200))

    at.run()
    #at.port.print_log()
    
    #print a.plot()
    a_plot = stk.StockPlot(stk.StockPlotCell((a.Cs,a.dates)))
    a_plot.addSimple(stk.StockPlotCell( calc.sma((a.Cs, a.dates), 200),overlay=True))
    a_plot.addSimple(stk.StockPlotCell( calc.sma((a.Cs, a.dates), 50),overlay=True))
    a_plot.addSimple(stk.StockPlotCell( at.get_buy_plot_cell(),overlay=True,color='go'))
    a_plot.addSimple(stk.StockPlotCell( at.get_sell_plot_cell(),overlay=True,color='ro'))
   
    a_plot.addSimple(stk.StockPlotCell( calc.sma((a.Vs,a.dates) , 5)))
    a_plot.addSimple(stk.StockPlotCell( calc.obv((a.Cs,a.Vs,a.dates))))
    #a_plot.addSimple(stk.StockPlotCell( stkCalc.perc_diffs((a.get_close_list(), a.get_date_list()))))
    a_plot.addSimple(stk.StockPlotCell( at.get_total_value_plot_cell()))
   
   
    a_plot.plot()



