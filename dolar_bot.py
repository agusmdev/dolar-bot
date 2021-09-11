import requests
import json
import os

def check_previous(func):
    def f(self, *args, **kwargs):
        with open('prev.json') as f:
            prev_config = json.load(f)
        is_eq = all(i == j for i, j in zip(prev_config.values(), self.json().values()))
        print(prev_config)
        print()
        print(self.json())
        if is_eq:
            exit(1)
        return func(self, *args, **kwargs)
    return f


class Dolar:
    def __init__(self, api_url, chat_id, tgm_token, rate=15):
        self.chat_id = chat_id
        self.api_url = api_url
        self.tgm_token = tgm_token
        self.buy, self.sell, self.avg = self.get_usd_price()
        self.rate = rate
        
    def get_usd_price(self):
        usd = requests.get(self.api_url).json()['blue']
        return usd['value_buy'], usd['value_sell'], usd['value_avg']
        
    def get_spread(self):
        return self.sell - self.buy

    def json(self):
        return self.__dict__
    
    def get_month_salary(self, hours):
        return self.rate * hours * self.avg

    def save_prev(self):
        with open('prev.json', 'w') as f:
            json.dump(self.json(), f, indent=4)
    
    @check_previous
    def notify(self, hours=160):
        usd = f"Dolar blue:\ncompra: {self.buy}\nventa: {self.sell}\npromedio: {self.avg}\nspread: {self.get_spread()}"
        msg = f"En un mes de {hours} horas a {self.rate} por hora, el salario es: {self.get_month_salary(hours)}"
        try:
            requests.post(f"https://api.telegram.org/bot{self.tgm_token}/sendMessage",
                          data={'chat_id': self.chat_id, 'text': f"{usd}\n{msg}"})
            self.save_prev()
        except:
            self.notify(hours=hours)


if __name__ == '__main__':
    chat_id = os.getenv("CHAT_ID")
    tgm_token = os.getenv("TGM_TOKEN")
    api_url = os.getenv("API_URL")
    d = Dolar(api_url, chat_id, tgm_token, rate=20)
    d.notify(hours=166)