# Analyzing the gains of current plan
import pandas as pd

def getPortPrices(allocation):    
    
    print('\nReading fund data...')   
    fundPrices = pd.read_csv('PRICES.csv', parse_dates = True, index_col = 'DATE')
    chosenFunds = fundPrices.filter(items=allocation.index)
    
    p = []
    isins = allocation.index
    
    print('Calculating portfolio aggregated price...\n')
    for index, row in chosenFunds.iterrows():    
        for i in isins: p.append([pd.to_datetime(index), float(row[i]*allocation[i])]);
    
    portfolio = pd.DataFrame(p, columns=list(['DATES','PRICES']), dtype=float)
    pd.to_numeric(portfolio['PRICES'])
    pd.to_datetime(portfolio['DATES'], errors='coerce')
    
    portfolio['DATES'].dropna()
    portfolio = portfolio.groupby('DATES')['PRICES'].sum()
    portGAINS = portfolio.pct_change().dropna()
    
    print('STD: {}%'.format(round(100*portGAINS.std(),5)))
    print('Mean: {}%'.format(round(100*portGAINS.mean(),5)))
    print('Sharpe: {}'.format(round(portGAINS.std()/portGAINS.mean(),2)))
    
    return portfolio

def run_allocator():
	print('Getting aggregated portfolio prices:')
	fundAlloc = pd.read_csv('FUND LIST.csv', index_col='Fund Name')
	fundAlloc = fundAlloc[['ISIN']]
	fundAlloc['ALLOCATION'] = 1/len(fundAlloc['ISIN'])

	pAlloc = fundAlloc.filter(items=['ISIN', 'ALLOCATION']).loc[(fundAlloc['ALLOCATION'] != 0.00) & (fundAlloc.index != 'Total')].groupby('ISIN')['ALLOCATION'].sum()
	x = getPortPrices(pAlloc).pct_change()*100

	isin = fundAlloc['ISIN']
	aBench = pd.DataFrame({'ISIN':isin, 'ALLOCATION':round(1/len(isin), 3)}).groupby('ISIN')['ALLOCATION'].sum()
	xx = getPortPrices(aBench).pct_change()*100

	comparison = pd.DataFrame({'PORTFOLIO':x.rolling(60).mean(), 'SEB BENCH':xx.rolling(60).mean(), 'CORR Portfolio vs SEB BENCH':x.rolling(60).corr(xx)}, index=x.index)
	
	return comparison
