import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

class dvlaAuction:
    def __init__(self, id: str) -> None:
        self.id = id

        soup = self._get_data()
        lot_nos, regs, starting_prices, prices, lengths, end_times = self._parse_soup(soup)
        pandasDB = self._lists_to_pandas(lot_nos, regs, starting_prices, prices, lengths, end_times, ["lot_no", "reg", "starting_price", "current_price", "length", "end_time"])
        print(f"DEBUG | pandasDB generated")
        pandasDB.to_excel(f"{self.id}.xlsx")
        print(f"DEBUG | Saved as {self.id}.xlsx")

    def _get_data(self):
        resp = requests.get(f"https://dvlaauction.co.uk/auction/{self.id}/")
        print(f"DEBUG | Request OK: {resp.ok} | Request Status Code: {resp.status_code}")
        soup = BeautifulSoup(resp.content, features="html.parser")
        return soup
    
    def _parse_soup(self, soup: BeautifulSoup):
        recordList = soup.find_all("tr", class_="record record-lot")
        
        lot_nos = []
        regs = []
        starting_prices = []
        prices = []
        lengths = []
        end_times = []

        for record in recordList:
            lot_no = self._ints_from_str(record.find("td", class_="field-id unit unit-id data-id").text)
            reg = record.find("td", class_="field-name data-text")["data-sort"]
            starting_price = record.find("td", class_="field-reserve data-gbp")["data-sort"]
            price = record.find("td", class_="field-current-price data-gbp")["data-sort"]
            end_time = datetime.utcfromtimestamp(int(record.find("td", class_="field-end-time data-datetime")["data-sort"])).strftime("%Y-%m-%d %H:%M:%S")
            length = len(reg)

            lot_nos.append(lot_no)
            regs.append(reg)
            starting_prices.append(starting_price)
            prices.append(price)
            lengths.append(length)
            end_times.append(end_time)

        return lot_nos, regs, starting_prices, prices, lengths, end_times
    
    def _ints_from_str(self, string: str) -> list[int]:
        return [int(s) for s in string.split() if s.isdigit()]
    
    def _lists_to_pandas(self, list1, list2, list3, list4, list5, list6, columnNames) -> pd.DataFrame:
        return pd.DataFrame({
            columnNames[0]: list1,
            columnNames[1]: list2,
            columnNames[2]: list3,
            columnNames[3]: list4,
            columnNames[4]: list5,
            columnNames[5]: list6,
        })

dvlaAuction("B260")