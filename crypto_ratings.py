from lxml import html
import requests

""" risk levels 

0 = penny stock risky
1 = very risky
2 = moderately risky
3 = risky
4 = not that risky
5 = only kind of risky

progress levels

importance levels

10 = Can be built on & can support ICOs, both not yet
7 =  Only doing one of the two
5 = Current doing both
0 = Can't do either

"""

coins = {'Cardano':'ADA','Ethereum':'ETH','Bitcoin':'BTC','Ripple':'XRP','Wancoin':'WAN','ICON':'ICX','Zilliqa':'ZIL','RChain':'RHOC','Ontology':'ONT'}
types = {'Cardano':'coin','Ethereum':'coin','Bitcoin':'coin','Ripple':'coin','Wancoin':'token','ICON':'token','Zilliqa':'token','RChain':'token','Ontology':'token'}
risks = {'Cardano':3,'Ethereum':4,'Bitcoin':5,'Ripple':4,'Wancoin':3,'ICON':3,'Zilliqa':3,'RChain':3,'Ontology':3}
progression = {'Cardano':3,'Ethereum':8,'Bitcoin':9,'Ripple':8,'Wancoin':5,'ICON':5,'Zilliqa':5,'RChain':3,'Ontology':5}
importances = {'Cardano':10,'Ethereum':5,'Bitcoin':3,'Ripple':7,'Wancoin':10,'ICON':5,'Zilliqa':5,'RChain':5,'Ontology':5}
sim_mcs = {'Cardano':'Ethereum','Ethereum':'Bitcoin','Bitcoin':'Bitcoin','Ripple':'Ethereum','Wancoin':'Ripple','ICON':'Cardano','Zilliqa':'Cardano','RChain':'Cardano','Ontology':'Cardano'}
exchanges = ['binance','kucoin','poloniex','gate-io','bitstamp','kraken','hitbtc','bittrex','bitfinex','bithumb','huobi','okex','upbit','cryptopia','coinone']
exchange_points = 10
ath_upside_points = 10
progress_points = 10
importance_points = 10
risk_points = 5
sim_upside_points = 10
possible_points = exchange_points + ath_upside_points + risk_points + progress_points + importance_points + sim_upside_points

class Crypto:

	def __init__(self,name,symbol,typeof,curr_price,curr_mc,ath_price,sim_mc,num_exchange,importance,progress,risk,rating):
		self.name = name
		self.symbol = symbol
		self.typeof = typeof 
		self.curr_price = curr_price
		self.curr_mc = curr_mc
		self.ath_price = ath_price
		self.ath_upside = (ath_price/curr_price)
		self.sim_mc = sim_mc
		self.sim_upside = sim_mc/curr_mc
		self.num_exchange = num_exchange
		self.importance = importance
		self.progress = progress
		self.risk = risk
		self.rating = rating

	def getNumExchanges(self):
		page = requests.get('https://coinmarketcap.com/currencies/'+ self.name +'/#markets')
		content = html.fromstring(page.content)
		total_num_exchanges = 0
		for i in range(0,len(exchanges)):
			amount = content.xpath('//a[@href="/exchanges/'+exchanges[i]+'/"]/text()')
			if(len(amount)>0):
				total_num_exchanges = total_num_exchanges + 1
		self.num_exchange = total_num_exchanges

	def getPageContent(self):
		pass

	def getPrices(self):
		page = requests.get('https://www.livecoinwatch.com/price/'+self.name+'-'+self.symbol)
		content = html.fromstring(page.content)

		price_array = content.xpath('//div[@class="sub header price colored"]/text()')
		self.curr_price = price_array[0].replace("$","")

		mc_array = content.xpath('//div[@class="sub header price"]/text()')
		self.curr_mc = mc_array[0].replace("$","")

		ath_array = content.xpath('//span[@id="ath"]/text()')
		self.ath_price = ath_array[0].replace("$","")

		self.ath_upside = (float(self.ath_price.replace(",",""))/float(self.curr_price.replace(",","")))

		similar_page = requests.get('https://www.livecoinwatch.com/price/'+sim_mcs[self.name]+'-'+coins[sim_mcs[self.name]])
		similar_content = html.fromstring(similar_page.content)
		similar_mc_array = similar_content.xpath('//div[@class="sub header price"]/text()')
		self.sim_mc = similar_mc_array[0].replace("$","")
		self.sim_upside = float(self.sim_mc.replace(",",""))/float(self.curr_mc.replace(",",""))


	def allStats(self):
		return self.name + ' ' + self.symbol + ' ' + str(self.curr_price) + ' ' + self.typeof + ' ' + str(self.num_exchange) + ' ' + str(self.curr_mc) + ' ' + str(self.ath_price) + ' ' + format(self.ath_upside, '.2f') + ' ' + str(self.risk) + ' ' + str(self.sim_mc) + ' ' + str(self.sim_upside)

	def getRating(self):

		total_points = ((len(exchanges)-self.num_exchange)/len(exchanges)) * exchange_points

		if(self.ath_upside>ath_upside_points):
			total_points += ath_upside_points
		else:
			total_points += self.ath_upside

		total_points += self.risk

		total_points += progress_points-self.progress

		total_points += self.importance

		if(float(self.sim_upside)>=100):
			total_points += 12
		elif((float(self.sim_upside)>=50.0) & (float(self.sim_upside)<100.0)):
			total_points += 10
		elif((float(self.sim_upside)>=10.0) & (float(self.sim_upside)<50.0)):
			total_points += 8
		elif((float(self.sim_upside)>=5.0) & (float(self.sim_upside)<10.0)):
			total_points += 5
		else: total_points += 3

		total_points += (5000000000.0/(float(self.curr_mc.replace(",","")))) # multiple to $5 Billion


		self.rating = (total_points/possible_points)*100


def main():


	for name,symbol in coins.items():
		coin = Crypto(name,symbol,types[name],1,1,0,0,10,importances[name],progression[name],risks[name],0)
		coin.getNumExchanges()
		coin.getPrices()
		coin.getRating()
		#print(coin.allStats())
		#print(format(coin.rating, '.2f'))
		#print(coin.__dict__)
		rate = ""
		if(coin.rating>=80.0):
			rate = "strong buy"
		elif((coin.rating>=70.0) & (coin.rating<80.0)):
			rate = "buy"
		print(coin.name + ' ' + format(coin.rating, '.2f') + '% ' + rate)


main()