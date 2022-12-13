import locale
from datetime import date
import csv
import sys

import babel.numbers

money = 0.0                 # Staring money
investing_money = 100.0     # money to invest
frequency_days = 15         # you receive that money each 
increase_percentage = 0.1   # increase investing money percentage
increase_months = 12        # increase the investing amount each 12 months
risk_tolerance = 0.1        # risk tolerance percentage

# Do not touch this: 
shares = 0
last_day = None
days = 0

investing_times = 0
hard_earned_money = 0.0

dividends_earned = 0.0
dividends_received_times = 0
dividends_high = 0.0
dividends_low = 100.0
dividends_average = 0.0
useDividendsPercentage = True
useDividends = True

last_shares_value = 0.0

last_increase = None
increase_amounts = 0

first_date = None
last_date = None

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple

class DateType:
    separator = "/" # / or -
    year_pos = 2
    month_pos = 0
    day_pos = 1

    isYearComplet = True # 2021 or 21

class TradingDay:
    def __init__(self, date:date, open:float, high:float, low:float, close:float):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close


def formatMoney(money:float)->str:
    return babel.numbers.format_currency(money, 'USD', locale='en_US')

def diff_month(d1:date, d2:date)->int:
    return (d1.year - d2.year) * 12 + d1.month - d2.month

# 01/13/2022
def getDateTemp(dateStr: str)->date:
    ls = dateStr.split("/")
    return date(int(ls[2]), int(ls[0]), int(ls[1]))

# 01/13/22
def getDatePrices(dateStr: str)->date:
    ls = dateStr.split("/")
    return date(int(ls[2])  + 2000, int(ls[0]), int(ls[1]))

# 2022-01-13
def getDateDividends(dateStr: str)->date:
    ls = dateStr.split("-")
    return date(int(ls[0]), int(ls[1]), int(ls[2]))

def processDividendsPercentage(day:TradingDay, dividends):
    global dividends_received_times, dividends_average, dividends_high, dividends_low, dividends_earned
    global money

    try:
        dividends_perc =  float(dividends[str(day.date.__hash__())]) / 100 # get the dividends percentage
        if dividends_high < dividends_perc:
            dividends_high = dividends_perc
        if dividends_low > dividends_perc:
            dividends_low = dividends_perc

        dv = dividends_perc * shares * day.open # dividends to receive
        dividends_earned += dv # report how much you have earned doing this
        money += dv # add that to your money

        if(dv > 0):
            print(O+str(day.date),
            "Received dividends:", str(round(dividends_perc * day.open, 2)), "per share", str(round(dividends_perc * 100, 2))+"%",
            "total", formatMoney(dv),
            "with", str(shares), "shares",
            "at", formatMoney(day.open), "share price",
            "money:", formatMoney(money - dv) + "->", formatMoney(money)+W)

        dividends_average += dividends_perc
        if dv > 0:
            dividends_received_times += 1
    except:
        pass

def processDividendsWithValues(day:TradingDay, dividends):
    global dividends_received_times, dividends_average, dividends_high, dividends_low, dividends_earned
    global money

    try:
        dividends_value =  float(dividends[str(day.date.__hash__())]) # get the dividends value
        dividends_perce = dividends_value / day.open
        if dividends_high < dividends_perce:
            dividends_high = dividends_perce
        if dividends_low > dividends_perce:
            dividends_low = dividends_perce

        dv = dividends_value * shares # dividends to receive
        dividends_earned += dv # report how much you have earned doing this
        aux_money = money
        money += dv # add that to your money

        if(dv > 0):
            print(O+str(day.date),
            "Received dividends:", formatMoney(dividends_value), "per share", str(round(dividends_perce * 100, 2))+"%",
            "total", formatMoney(dv),
            "with", str(shares), "shares",
            "at", formatMoney(day.open), "share price",
            "money:", formatMoney(aux_money) + "->", formatMoney(money)+W)

        dividends_average += dividends_perce
        if dv > 0:
            dividends_received_times += 1
    except:
        pass

def process(day:TradingDay, dividends):
    global hard_earned_money, shares, investing_times, investing_money
    global first_date, last_date, last_increase, increase_amounts
    global last_day, last_shares_value, money


    # look if it is time for you to receive your dividends
    if useDividendsPercentage:
        processDividendsPercentage(day, dividends)
    elif useDividends:
        processDividendsWithValues(day, dividends)

    # if you have enough money to buy, then buy
    if money >= day.low:
        # buy
        buy_shares = int(money / day.low) # amount of shares that can be bought
        aux_money = money
        money = money - (day.low * buy_shares) # substrat the money
        shares += buy_shares # add shers to the total
        if buy_shares > 0: 
            print(G+str(day.date), 
            "Bought", str(buy_shares), "shares at", formatMoney(day.low), 
            "total shares:", str(shares), "value:", formatMoney(shares * day.low),
            "money", formatMoney(aux_money) +"->", formatMoney(money)+W)
            investing_times += 1 # if you bought a share then report it


    # if it is the first day
    if last_day is None:
        last_increase = day.date
        first_date = day.date
        last_day = day.date
        return 

    ######
    delta_increse = diff_month(day.date, last_increase)
    delta = day.date - last_day

    # look if you need to increase the amount of money you invest    
    if delta_increse >= increase_months:
        aux_investing_money = investing_money
        investing_money = investing_money * (1 + increase_percentage)
        increase_amounts += 1
        
        print(B+str(day.date) + " Increasing investing money from " + formatMoney(aux_investing_money) + " to " + formatMoney(investing_money)+W)

        last_increase = day.date

    # look if the time that you need to invest your money has past
    if delta.days >= frequency_days:
        hard_earned_money += investing_money
        aux_money = money
        money += investing_money

        last_day = day.date

        print(P+str(day.date) + " Saving " + formatMoney(investing_money) + "  " + formatMoney(aux_money) +"->" + formatMoney(money)+W)


    last_shares_value = day.close
    last_date = day.date

def main():
    global useDividendsPercentage, useDividends
    args = sys.argv[1:]
    
    # if you don't want to use dividends --nd
    if args.__contains__("--nd"):
        print("Not using dividends")
        useDividends = False
    # if you don't want to use dividends percentage --ndp
    if args.__contains__("--ndp"):
        print("Using dividends values")
        useDividendsPercentage = False

    


    with open('historicalPrices_VOO.csv') as csv_prices, open('multpl-voo_div_yield_month.csv') as csv_dividends:
        csv_reader = csv.reader(csv_prices, delimiter=',')
        line_count = 0

        # prices to list
        data = list(csv_reader)

        # dividends to dict
        data_dividends = {str(getDateTemp(row[0]).__hash__()):row[1] for row in csv.reader(csv_dividends, delimiter=',') if row[0] != "Date"}
        for row in reversed(data):
            if line_count < (len(data) - 1): # -1 headers
                # Date 1, Open 2, High 3, Low 4, Close 5 
                tradingDay = TradingDay(getDatePrices(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]))
                process(tradingDay, data_dividends)
            line_count += 1

        # print(f'Processed {line_count} lines.')

    print("\n\n######### Scenario #########")
    print("You save", formatMoney(investing_money), "dolars each", frequency_days, "days")
    print("Each", increase_months, "months you increase", increase_percentage , "% of what you invest")
    print("You try to buy all the shares that you can each day with that money")
    
    print("\n\n######### Results #########")
    print("From", first_date, "to", last_date, "years:", (last_date - first_date).days/365)
    print("Amount of times you could buy at lest one shere:", investing_times)
    print("Amount of times you received dividiends:", dividends_received_times)
    print("Last close day:", formatMoney(last_shares_value))
    print("You are investing", formatMoney(investing_money), "after", increase_amounts, "increases of", increase_percentage*100,"% one each", increase_months, "months")
    print("Dividiends earend:", formatMoney(dividends_earned))
    print("Dividends high:", dividends_high * 100, "%")
    print("Dividends low:", dividends_low * 100, "%")
    if dividends_received_times > 0:
        print("Dividends average:", (dividends_average / dividends_received_times) * 100, "%")
    else:
        print("Dividends average:", 0, "%")
    print("Money left:", formatMoney(money))
    print("Amount of shares you own:", shares)
    print("Value of shares:", formatMoney(last_shares_value * shares))
    print("Hard earned money:", formatMoney(hard_earned_money))
    gains = money + (last_shares_value * shares) - hard_earned_money
    print("Gains", formatMoney(gains), "growth:", round(gains/hard_earned_money, 4) * 100, "%")
    print("Total money you own", formatMoney(money + (last_shares_value * shares)))


if __name__ == '__main__':
    main()