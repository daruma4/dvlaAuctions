import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import os

class dvlaAuction:
    def __init__(self, id: str, space_incl: bool) -> None:
        self.id = id
        self.dir = os.path.abspath("")
        self.results_dir = os.path.join(self.dir, "auction_results")
        self.space_include_reg = space_incl

    def run(self):
        soup = self._get_data()
        if not soup:
            return
        lot_nos, regs, starting_prices, prices, lengths, categories = self._parse_soup(soup)
        pandasDB = self._lists_to_pandas(list(zip(lot_nos, regs, starting_prices, prices, lengths, categories)), ["lot_no", "reg", "starting_price", "current_price", "length", "category"])
        
        print(f"DEBUG | pandasDB generated")
        pandasDB.to_excel(os.path.join(self.results_dir, f"{self.id}.xlsx"))
        print(f"DEBUG | Saved {os.path.join(self.results_dir, f'{self.id}.xlsx')}")

    def _get_data(self):
        resp = requests.get(f"https://dvlaauction.co.uk/auction/{self.id}/")
        print(f"DEBUG | Auction ID: {self.id} | Request OK: {resp.ok} | Request Status Code: {resp.status_code}")
        if resp.status_code == 404:
            return
        soup = BeautifulSoup(resp.content, features="html.parser")
        return soup
    
    def _parse_soup(self, soup: BeautifulSoup):
        recordList = soup.find_all("tr", class_="record record-lot")
        
        lot_nos = []
        regs = []
        starting_prices = []
        prices = []
        lengths = []
        categories = []

        for record in recordList:
            lot_no = self._ints_from_str(record.find("td", class_="field-id unit unit-id data-id").text)
            if self.space_include_reg:
                reg = record.find("td", class_="field-name data-text").getText().lstrip().rstrip()
            else:
                reg = record.find("td", class_="field-name data-text")["data-sort"]
            starting_price = record.find("td", class_="field-reserve data-gbp")["data-sort"]
            price = record.find("td", class_="field-current-price data-gbp")["data-sort"]
            category = self._text_cleaner(record.find("td", class_="field-lot-categories").text)
            length = len(reg)

            lot_nos.append(lot_no)
            regs.append(reg)
            starting_prices.append(starting_price)
            prices.append(price)
            lengths.append(length)
            categories.append(category)

        return lot_nos, regs, starting_prices, prices, lengths, categories
    
    def _ints_from_str(self, string: str) -> list[int]:
        return [int(s) for s in string.split() if s.isdigit()]
    
    def _text_cleaner(self, string: str) -> str:
        text = string
        text = text.replace("\r", "").replace("\n", "").replace(" ", "")
        return text
    
    def _lists_to_pandas(self, listZipped, columnNames) -> pd.DataFrame:
        return pd.DataFrame(listZipped, columns=columnNames)