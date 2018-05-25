from bs4 import BeautifulSoup
import requests
import pandas as pd

#Getting list of funds:
fundList = requests.get('https://ibanka.seb.lv/cgi-bin/ipank/ipank.p?act=VPFOND')
soup = BeautifulSoup(fundList.text, 'html.parser')

isins = []

#Listing all fund names and ISIN codes
for tr in soup.find_all('tr'):
    if len(tr)>10 :
        fundName = tr.find_all('td')[1].text
        sep = str(tr.a).find('isin=') + 5
        isins.append([fundName, str(tr.a)[sep:sep+12]])

funds = pd.DataFrame(isins, columns=list(['Fund Name','ISIN']))
print('List of ISINs and fund names gathered!\n')

#Getting the prices for each ISIN
prices = []
for isin in isins:
    temp = []
    pricePage = requests.get('https://ibanka.seb.lv/cgi-bin/ipank/ipank.p?sesskey=&lang=LAT&act=VPFONDINFO&isin=' + isin[1])
    soup = BeautifulSoup(pricePage.text, 'html.parser')

    txt = str(soup.find_all('script'))[str(soup.find_all('script')).find('function convertDate(date) {')+159:str(soup.find_all('script')).find('initChart(min,seriesdata,isin,valuuta')-1]
    txt = txt.replace('\n','')
    txt = txt.replace('convertDate(','')
    txt = txt.replace(')','')
    txt = txt.replace('removeNegatives(','')
    txt = txt[1:txt.find(',isin')]

    temp = txt.split('],[')

    if len(temp)>1000:
        for p in temp:
            str(p).replace(']','')
            str(p).replace('[','')
            if len(p)>0:
                prices.append([isin[0], isin[1], str(p[1:5]) + '-' + str(p[5:7]) + '-' + str(p[7:9]), str(p[11:])])
        
    print('Prices for {} have been gathered!'.format(isin[0]))

#Some basic data cleaning:
print('\nCleaning prices...')
for p in prices:
    p[3] = p[3].replace(']','')

data = pd.DataFrame(prices, columns=list(['Fund Name','ISIN','DATE','PRICE']))
data['PRICE'].astype('float64')

result = data.pivot(index = 'DATE', columns = 'ISIN', values = 'PRICE')
result = result.apply(pd.to_numeric, errors='ignore')
result = result.dropna(how = 'any')

gains = result.pct_change()
correlations = gains.corr()
riskSTD = gains.std()

#Saving everything to one MS Excel file
print('Saving data to MS Excel file')
with pd.ExcelWriter('D:\Development\Python Projects\FONDI\SEB funds.xlsx') as pdExcel:
    result.to_excel(pdExcel, 'DATA')
    gains.to_excel(pdExcel, 'YIELDS')
    funds.to_excel(pdExcel, 'FUND LIST')
    correlations.to_excel(pdExcel, 'CORRs')
    riskSTD.to_excel(pdExcel, 'RISKS')
    pdExcel.save()

print('\nImport process completed!')
