from sympy import symbols, Eq, solve
from bitmex import bitmex
import sys
import json
import os

bitmex_api_key = 'SAETUP'
bitmex_api_secret = 'SAETUP'
bitmex_client = bitmex(test=False, api_key=bitmex_api_key, api_secret=bitmex_api_secret)
balance = bitmex_client.User.User_getWalletHistory().result()[0][0]['walletBalance']/100000000


def position_size(entry, stop, balance, risk):
    x = symbols('x')
    if target > entry:
        target_value = (1/target)+((1/target)*takerFee)
        stop_value = (1/stop)+((1/stop)*takerFee)
        if order_type == 'Limit':
            entry_value = (1/entry)-((1/entry)*makerFee)
            eq1 = Eq((x*(entry_value - stop_value)) + (balance*risk)) 
        else:
            entry_value = (1/entry)-((1/entry)*takerFee)
            eq1 = Eq((x*(entry_value - stop_value)) + (balance*risk))
    elif target < entry:
        target_value = (1/target)-((1/target)*takerFee)
        stop_value = (1/stop)-((1/stop)*takerFee)
        if order_type == 'Limit':
            entry_value = (1/entry)+((1/entry)*makerFee)
            eq1 = Eq((x*(stop_value - entry_value)) - (balance*risk))
        else:
            entry_value = (1/entry)+((1/entry)*takerFee)
            eq1 = Eq((x*(stop_value - entry_value)) - (balance*risk))
    size = solve(eq1)
    size = [ '%.0f' % elem for elem in size ]
    size = size[0]
    return size, entry_value, stop_value, target_value


def risk_amount_XBT(entry_value, stop_value, size):
    risk_amount = (size*(entry_value - stop_value))
    risk_amount = float(round(risk_amount, 8))
    return risk_amount


def reward_amount_XBT(entry_value, target_value, size):
    reward_amount = (size*(target_value - entry_value))
    reward_amount = float(round(reward_amount, 8))
    return reward_amount


def breakeven_XBT(entry_value, takerFee):
    y = symbols('y')
    eq2 = Eq(((1/y)+((1/y)*takerFee)) - entry_value)
    if target < entry:
        eq2 = Eq(((1/y)-((1/y)*takerFee)) - entry_value)
    breakeven = solve(eq2)
    breakeven = [ '%.2f' % elem for elem in breakeven ]
    return breakeven

def r(reward_amount, risk_amount):
    r_r = reward_amount/risk_amount
    return r_r

def initiate_trade(contract, size, entry, target, stop):
    if len(bitmex_client.Order.Order_getOrders(symbol = contract, filter = json.dumps({'open': 'true'})).result()[0]) > 0:
        cancel_existing_prders = bitmex_client.Order.Order_cancelAll(symbol=contract).result()
    if order_type == order_types[0]: 
        entry_placement = bitmex_client.Order.Order_new(symbol=contract, orderQty=size, ordType='Market').result()
        exit_placement = bitmex_client.Order.Order_new(symbol=contract, price=target, execInst='ReduceOnly', orderQty=(size*-1), ordType='Limit').result()
        stop_placement = bitmex_client.Order.Order_new(symbol=contract, stopPx=stop, execInst=str('LastPrice, ReduceOnly'), orderQty=(size*-1), ordType='Stop').result()

    else:
        entry_placement = bitmex_client.Order.Order_new(symbol=contract, orderQty=size, price=entry).result()
        if target < entry:
            stop_limit_trigger = float(float(entry)+0.5)
        else:
            stop_limit_trigger = float(float(entry)-0.5)
        exit_placement = bitmex_client.Order.Order_new(symbol=contract, stopPx=stop_limit_trigger, price=target, execInst=str('LastPrice, ReduceOnly'), orderQty=(size*-1), ordType='StopLimit').result()
        stop_placement = bitmex_client.Order.Order_new(symbol=contract, stopPx=stop, execInst=str('LastPrice, ReduceOnly'), orderQty=(size*-1), ordType='Stop').result()

def current_position(contract):
    open_position = bitmex_client.Position.Position_get(filter = json.dumps({'symbol': str(contract), 'isOpen': True})).result()[0][0]
    open_orders = bitmex_client.Order.Order_getOrders(symbol=contract, filter = json.dumps({'open': 'true'})).result()[0]
    if len(bitmex_client.Order.Order_getOrders(symbol=contract, filter = json.dumps({'open': 'true', 'ordType': ['Limit', 'MarketIfTouched', 'StopLimit', 'LimitIfTouched']})).result()[0]) != 0:
        close_order = bitmex_client.Order.Order_getOrders(symbol = str(contract), filter = json.dumps({'open': 'true', 'ordType': ['Limit', 'MarketIfTouched', 'StopLimit', 'LimitIfTouched']})).result()[0]
        if close_order[0]['price'] is not None:
            close_price = format(close_order[0]['price'], '.1f')
        else:
            close_price = format(close_order[0]['stopPx'], '.1f')
    else:
        close_order = 'No Close Order Set'
        close_price = 'No Close Order Set'
    if len(bitmex_client.Order.Order_getOrders(symbol=contract, filter = json.dumps({'open': 'true', 'ordType': ['Stop', 'TrailingStop']})).result()[0]) > 0:
        stop_order = bitmex_client.Order.Order_getOrders(symbol=contract, filter = json.dumps({'open': 'true', 'ordType': ['Stop', 'TrailingStop']})).result()[0]
        stop_price = format(stop_order[0]['stopPx'], '.1f')
    else:
        stop_order = 'NO STOP SET!!!'
        stop_price = 'NO STOP SET!!!'
    if open_position['currentQty'] > 0:
        direction = 'Long'
    else:
        direction = 'Short'

    entry = format(open_position['avgEntryPrice'], '.1f')
    market_price = format(bitmex_client.Instrument.Instrument_get(filter = json.dumps({'symbol': str(contract)})).result()[0][0]['lastPrice'], '.1f')

    size = open_position['currentQty']
    realisedPnL = format((open_position['realisedGrossPnl']/100000000), '.8f')
    unrealisedPnL = format((open_position['unrealisedGrossPnl']/100000000), '.8f')
    my_position = f"""
    Symbol: {contract}
    Direction: {direction}
    Size: {size}
    Entry: {entry}
    Stop: {stop_price}
    Target: {close_price}
    Market_Price: {market_price}
    Daily Realised_PNL: {realisedPnL}
    Current Unrealised_PNL: {unrealisedPnL}
    """

    return my_position, close_order, stop_order, stop_price, close_price, size

########################################################################################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

"""

print('Welcome to MEXecutioner'+'\n')
print('\n'+'Enter trade limit. Enter 0 to disable trade counter'+'\n')
"""

#TODO: REFACTOR THE WHOLE FILE
# This is built for CLI use ########################################################################
########################################################################################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

total_trades = int(input('\n'))
trade_counter = 0
valid_ticks = tuple(list(range(10)))
contract = 'XBTUSD'

while True:
    if trade_counter > 0:
        print('You have executed '+str(trade_counter)+' trades in this loop'+'\n'+
             'You have '+str(total_trades-trade_counter)+' trades remaining'+'\n')
    step1_options = {0: 'Open Positions', 1: 'Plan New Trade'}
    while True:
        try:
            print('Please choose an option below to get started' + '\n')
            for k, v in step1_options.items():
                    print(k, ': ', v)
            step1 = int(input('\n'))
        except (IndexError, ValueError):
            print('Selection invalid. Try again')
            continue
        else:
            break
    if step1 == 1:
        while True:
            try:
                order_types = {0:'Market', 1:'Limit'}
                order_type = int(input('Choose Order Type for Entry'+'\n'+str(order_types)+'\n'))
                order_type = order_types[order_type]
                print('Entry Order Type: ' + str(order_type))
            except (IndexError, ValueError):
                print('Entry Order Type selection must be a number 0-1. Try Again')
                continue
            else:
                break
        while True:
            stop = str(input('Stop Market Price: '))
            if '.' not in stop and stop[-1] not in str({valid_ticks}) or '.' in stop and stop[-1] not in str({0, 5}):
                print('Invalid Tick Size')
                continue
            else:
                stop = float(stop)
                break
        while True:
            target = str(input('Target Price: '))
            if '.' not in target and target[-1] not in str({valid_ticks}) or '.' in target and target[-1] not in str({0, 5}):
                print('Invalid Tick Size')
                continue
            else:
                target = float(target)
                break
        while True:
                contract_data = bitmex_client.Instrument.Instrument_getActive().result()[0] 
                contract_data = next(item for item in contract_data if item["symbol"] == contract)
                tick_size = float(contract_data["tickSize"])
                bidPrice = float(contract_data['bidPrice'])
                askPrice = float(contract_data['askPrice'])
                makerFee = float(contract_data['makerFee'])
                takerFee = float(contract_data['takerFee'])
                if order_type == 'Limit':
                    entry = str(input('Limit Entry Price: '))
                    if '.' not in entry and entry[-1] not in str({valid_ticks}) or '.' in entry and entry[-1] not in str({0, 5}):
                        print('Invalid Tick Size')
                        continue
                    else:
                        entry = float(entry)
                        break
                else:
                    if stop > target:
                        entry = bidPrice
                        break
                    else:
                        entry = askPrice
                        break
        while True:
            try:
                risk = float(input('BTC Risk Percentage. Or 0 for 1x Short: '))/100
                if risk == 0:
                    risk = (stop - entry) / entry
                else:
                    None
            except ValueError:
                print('Risk must be expressed as integer or float. I.e. 3% is 3. 0.5% is 0.5. Or choose 0 for 1x Short')
                continue
            else:
                break
        balance = bitmex_client.User.User_getWalletHistory().result()[0][0]['walletBalance']/100000000
        position_size_1 = position_size(entry, stop, balance, risk)
        size = int(position_size_1[0])
        entry_value = float(position_size_1[1])
        stop_value = float(position_size_1[2])
        target_value = float(position_size_1[3])

        risk_amount = risk_amount_XBT(entry_value, stop_value, size)*-1

        reward_amount = reward_amount_XBT(entry_value, target_value, size)*-1

        r_r = r(reward_amount, risk_amount)
        r_r = format(r_r, '.2f')

        breakeven = breakeven_XBT(entry_value, takerFee)[0]

        loss_final_balance = balance - risk_amount
        loss_final_balance = round(loss_final_balance, 8)
        win_final_balance = balance + reward_amount
        win_final_balance = round(win_final_balance, 8)
        starting_usd = balance*entry
        starting_usd = round(starting_usd, 2)
        winning_usd = win_final_balance*target
        winning_usd = round(winning_usd, 2)
        losing_usd = loss_final_balance*stop
        losing_usd = round(losing_usd, 2)
        risk_amount = format(risk_amount, '.8f')
        reward_amount = format(reward_amount, '.8f')

        if target < entry:
            direction = 'Short'
        else:
            direction = 'Long'

        risk_percentage = str(round(risk*100, 1))+'%'

        trade_details = f"""
        Contract: {contract}
        Direction: {direction}
        BTC Percent Risk: {risk_percentage}
        Size: {size}
        Entry: {entry}
        Stop: {stop}
        Target: {target}
        Risk: {risk_amount} BTC
        Reward: {reward_amount} BTC
        R: {r_r}
        Breakeven: {breakeven}
        Starting Balance: {balance} / ${starting_usd}
        Winning Balance: {win_final_balance} / ${winning_usd}
        Losing Balance: {loss_final_balance} / ${losing_usd}
        """
        print(trade_details)

        while True:
            try:
                trade_execution = int(input('Do you wish to take this trade?'+'\n'+'All existing orders for '+str(contract)+' will be cancelled'+'\n'+'0:Yes, 1:No' + '\n'))
                if trade_execution == 0:
                    if total_trades != 0:
                        trade_counter += 1
                    if bitmex_client.Position.Position_get(filter = json.dumps({'symbol': str(contract)})).result()[0][0]['currentQty'] != 0:
                        bitmex_client.Order.Order_new(symbol=contract, orderQty=((bitmex_client.Position.Position_get(filter = json.dumps({'symbol': str(contract)})).result()[0][0]['currentQty'])*-1), ordType='Market').result()
                    else:
                        None
                    initiate_trade(contract, size, entry, target, stop)
                    print('TRADE EXECUTED')
                else:
                    print('TRADE NOT EXECUTED')
            except ValueError:
                print('Selection must be a number 0-1. Try Again')
                continue
            else:
                break

    elif step1 == 0:
        while True:
            try:
                open_position = current_position(contract)
                my_position = open_position[0]
                if open_position[1] != 'No Close Order Set':
                    close_orderID = open_position[1][0]['orderID']
                else:
                    close_orderID = open_position[1]
                if open_position[2] != 'NO STOP SET!!!':
                    stop_orderID = open_position[2][0]['orderID']
                else:
                    stop_orderID = open_position[2]
                stop_price = open_position[3]
                close_price = open_position[4]
                size = open_position[5]

                live_position = f"""Here is your current {contract} position
                {my_position}"""
                print(live_position)
            except IndexError:
                print('No Open Positions')
                break
            else:
                step2_options = {0: 'Close Position', 1: 'Amend Orders', 2: 'Take Profit', 3: 'Return to Start'}
                while True:
                    print(live_position)
                    try:
                        print('Please choose an option below' + '\n')
                        for k, v in step2_options.items():
                            print(k, ': ', v)
                        step2 = int(input('\n'))
                    except (IndexError, ValueError):
                        print('Selection invalid. Try again')
                        continue
                    else:
                        if step2 ==3:
                            break

                        elif step2 ==0:
                            bitmex_client.Order.Order_new(symbol=contract, orderQty=(size*-1), ordType='Market').result()
                            close_dialogue = f"""{contract} Position Closed"""
                            print(close_dialogue)
                            bitmex_client.Order.Order_cancelAll(symbol=contract).result()
                            cancel_dialogue = f"""{contract} Pending Orders Cancelled"""
                            print(cancel_dialogue)
                            break

                        elif step2 == 1:
                            new_stop_dialogue = f"""Input new Stop Price. Or choose '0' to continue"""
                            print(new_stop_dialogue)
                            new_stop = input('New Stop Price: ')
                            if '.' not in new_stop and new_stop[-1] not in str({valid_ticks}) or '.' in new_stop and new_stop[-1] not in str({0, 5}):
                                print('Invalid Tick Size')
                                continue
                            new_target_dialogue = f"""Input new Close Price. Or choose '0' to continue"""
                            print(new_target_dialogue)
                            new_target = input('New Close Price: ')
                            if '.' not in new_target and new_target[-1] not in str({valid_ticks}) or '.' in new_target and new_target[-1] not in str({0, 5}):
                                print('Invalid Tick Size')
                                continue

                            if new_stop == '0':
                                None
                            else:
                                if stop_price == 'NO STOP SET!!!':
                                    bitmex_client.Order.Order_new(symbol=contract, orderQty=(size*-1), stopPx=new_stop, execInst=str('LastPrice, ReduceOnly'), ordType='Stop').result()
                                else:
                                    bitmex_client.Order.Order_amend(orderID=stop_orderID, stopPx=new_stop).result()
                                    amend_stop_dialogue = f"""{contract} Stop Amended to {new_stop}"""
                                    print(amend_stop_dialogue)

                            if new_target == '0':
                                None
                            else:
                                if close_price == 'No Close Order Set':
                                    bitmex_client.Order.Order_new(symbol=contract, orderQty=(size*-1), price=new_target, execInst='ReduceOnly', ordType='Limit').result()
                                else:
                                    if bitmex_client.Order.Order_getOrders(symbol=contract, filter = json.dumps({'orderID': str(close_orderID)})).result()[0][0]['price'] is None:
                                        bitmex_client.Order.Order_amend(orderID=close_orderID, stopPx=new_target).result()
                                    else:
                                        bitmex_client.Order.Order_amend(orderID=close_orderID, price=new_target).result()
                                    amend_target_dialogue = f"""{contract} Close Amended to {new_target}"""
                                    print(amend_target_dialogue)

                            amended_position = current_position(contract)
                            amended_position = amended_position[0]
                            amended_position_dialogue = f"""Here is your updated {contract} position
                            {amended_position}"""
                            print(amended_position_dialogue)
                            break

                        elif step2 == 2:
                            take_profit = input('Input the percentage of your current position to close' + '\n')
                            take_profit_size = round(((size*(int(take_profit)/100))*-1), 0)
                            bitmex_client.Order.Order_new(symbol=contract, orderQty=take_profit_size, ordType='Market').result()
                            bitmex_client.Order.Order_cancelAll(symbol=contract).result()
                            if close_price == 'No Close Order Set':
                                None
                            else:
                                bitmex_client.Order.Order_new(symbol=contract, price=close_price, orderQty=((size-take_profit_size)*-1), execInst='ReduceOnly', ordType='Limit').result()
                            if stop_price == 'NO STOP SET!!!':
                                None
                            else:
                                bitmex_client.Order.Order_new(symbol=contract, stopPx=stop_price, orderQty=((size+take_profit_size)*-1), execInst=str('LastPrice, ReduceOnly'), ordType='Stop').result()                                
                            if take_profit_size > 0:
                                take_profit_dialogue = f"""{take_profit_size} {contract} contracts bought"""
                            else:
                                take_profit_dialogue = f"""{take_profit_size} {contract} contracts sold"""
                                print(take_profit_dialogue)

                            amended_position = current_position(contract)
                            amended_position = amended_position[0]
                            amended_position_dialogue = f"""Here is your updated {contract} position
                            {amended_position}"""
                            print(amended_position_dialogue)
                            break
                        break
                    break
                break
            break