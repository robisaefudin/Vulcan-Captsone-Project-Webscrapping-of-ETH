from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import numpy as np


#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data?start_date=2022-01-01&end_date=2023-03-30#panel')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table_body = soup.find('tbody', {'data-target': 'historical.tableBody'})
row = table_body.find_all('th', attrs={'class': 'font-semibold text-center', 'scope': 'row'})
row_length = len(row)

output_rows = [] #init

# loop through all rows in the table body
for row in table_body.find_all('tr'):
    
    # extract the date from the first cell
    date = row.find('th', {'class': 'font-semibold text-center', 'scope': 'row'}).text.strip()

    # extract data from the remaining cells
    data_cells = row.find_all('td', {'class': 'text-center'})
    market_cap = data_cells[0].text.strip()    #diurutkan dari 0. Ini untuk kolom 2
    volume = data_cells[1].text.strip()        # kolom 3
    open_price = data_cells[2].text.strip()    #4
    close_price = data_cells[3].text.strip()   #5

    # add the output row to the list
    output_rows.append((date, market_cap, volume, open_price, close_price))

# print the output rows
for row in output_rows:
    print(row)

#change into dataframe
df =pd.DataFrame(output_rows, columns= ['date', 'market_cap', 'volume', 'open_price', 'close_price'])
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(by='date')
df = df.set_index('date')


df['close_price'] = df['close_price'].replace('N/A', np.nan)
df['close_price'] = df['close_price'].fillna(method='bfill')
df.replace('[\$,]', '', regex=True, inplace=True)
df = df.apply(pd.to_numeric)

volume = df['volume']

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["volume"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = volume.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)