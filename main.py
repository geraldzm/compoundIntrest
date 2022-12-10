import locale
from datetime import date
import csv

money = 0.0                 # Staring money
investing_money = 100.0     # money to invest
frequency_days = 15         # you receive that money each 
increase_percentage = 0.1   # increase investing money percentage
increase_months = 12        # increase the investing amount each 12 months

# Do not touch this: 
shares = 0
last_day = None
days = 0

investing_times = 0
hard_earned_money = 0.0

dividends_earned = 0.0
dividends_received_times = 0
dividends_high = 0.0
dividends_low = 0.0
dividends_average = 0.0

last_shares_value = 0.0

last_increase = None
increase_amounts = 0

first_date = None
last_date = None

locale.setlocale(locale.LC_ALL, '' )
def formatMoney(money:float)->str:
    return locale.currency(money, grouping=True)

def diff_month(d1:date, d2:date)->int:
    return (d1.year - d2.year) * 12 + d1.month - d2.month

# 01/13/22
def getDatePrices(dateStr: str)->date:
    ls = dateStr.split("/")
    return date(int(ls[2])  + 2000, int(ls[0]), int(ls[1]))

# 2022-01-13
def getDateDividends(dateStr: str)->date:
    ls = dateStr.split("-")
    return date(int(ls[0]), int(ls[1]), int(ls[2]))

def process(row, dividends):
    global hard_earned_money, dividends_earned, shares, investing_times, investing_money
    global last_day, last_shares_value, money, dividends_received_times
    global first_date, last_date, last_increase, increase_amounts
    global dividends_high, dividends_low, dividends_average

    # Date 1, Open 2, High 3, Low 4, Close 5 
    open = float(row[1])
    high = float(row[2])
    low = float(row[3])
    close = float(row[4])

    current_day = getDatePrices(row[0])
    
    # if you have enough money to buy, then buy
    if money >= low:
        # buy
        buy_shares = int(money / low) # amount of shares that can be bought
        money = money - (low * buy_shares) # substrat the money
        shares += buy_shares # add shers to the total
        if buy_shares > 0: 
            investing_times += 1 # if you bought a share then report it

    # look if it is time for you to receive your dividends
    try:
        dividends_perc =  float(dividends[str(current_day.__hash__())]) / 100 # get the dividends percentage

        if dividends_high < dividends_perc:
            dividends_high = dividends_perc
        if dividends_low > dividends_perc:
            dividends_low = dividends_perc

        dv = dividends_perc * shares * open # dividends to receive
        dividends_earned += dv # report how much you have earned doing this
        money += dv # add that to your money

        dividends_average += dividends_perc
        dividends_received_times += 1

    except:
        pass

    # if it is the first day
    if last_day is None:
        last_dividends = current_day
        last_increase = current_day
        first_date = current_day
        last_day = current_day
        return 

    ######
    delta_increse = diff_month(current_day, last_increase)
    delta = current_day - last_day

    # look if you need to increase the amount of money you invest    
    if delta_increse >= increase_months:
        investing_money = investing_money * (1 + increase_percentage)
        increase_amounts += 1
        
        last_increase = current_day

    # look if the time that you need to invest your money has past
    if delta.days >= frequency_days:
        hard_earned_money += investing_money
        money += investing_money

        last_day = current_day


    last_shares_value = close
    last_date = current_day


def main():
    with open('historicalPrices.csv') as csv_prices, open('multpl-sp500_div_yield_month.csv') as csv_dividends:
        csv_reader = csv.reader(csv_prices, delimiter=',')
        line_count = 0

        # prices to list
        data = list(csv_reader)

        # dividends to dict
        data_dividends = {str(getDateDividends(row[0]).__hash__()):row[1] for row in csv.reader(csv_dividends, delimiter=',') if row[0] != "Date"}

        for row in reversed(data):
            if line_count < (len(data) - 1): # -1 headers
                process(row, data_dividends)
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
    print("Dividends average:", (dividends_average / dividends_received_times) * 100, "%")
    print("Money left:", formatMoney(money))
    print("Amount of shares you own:", shares)
    print("Value of shares:", formatMoney(last_shares_value * shares))
    print("Hard earned money:", formatMoney(hard_earned_money))
    print("Gains", formatMoney(money + (last_shares_value * shares) - hard_earned_money))
    print("Total money you own", formatMoney(money + (last_shares_value * shares)))


if __name__ == '__main__':
    main()