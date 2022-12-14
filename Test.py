import re
import pdfplumber

from unrar import rarfile
import zipfile
from consts import const
import os


def parse_pdf(path):
    with pdfplumber.open(path) as pdf:
        re1 = re.compile(r".*?保养.*?(\d+)")
        start_page = None
        end_page = None
        num_list = []
        for page in pdf.pages[4:8]:
            text = page.extract_text()
            ret = re1.findall(text)
            if len(ret) >= 2:
                for x in ret:
                    if int(x) >= len(pdf.pages) // 2:
                        num_list.append(int(x))
                break
        print(num_list)
        if len(num_list) > 0:
            tables = []
            table_settings = {
                "vertical_strategy": "text"
            }
            for page in pdf.pages[min(num_list):max(num_list)]:
                p = page.extract_tables(table_settings)
                tables.extend(p)
            data = []
            end_flag = False
            for table in tables:
                if table is None:
                    continue
                if end_flag:
                    break
                for tab in table:
                    if len(tab) >= 2:
                        if tab[0] is None or "保养" in tab[0]:
                            continue
                        if tab[0] == "序号" or re.match(r"[A-Z0-9]+", tab[0]):
                            continue
                        content = ""
                        start = 1
                        if len(tab) >= 3:
                            start = 2
                        for x in tab[start:]:
                            if x is None or re.match(r"/?\d+", x) or x == "I" or x == "R" or "●" in x:
                                continue
                            content += x
                        if content:
                            content = content.replace("\n", "")
                            title = ""
                            for x in tab[:start]:
                                if x == "" or x is None:
                                    continue;
                                title += x.replace("\n", "");
                            if "I" in title or "I" in content:
                                continue
                            data.append([title, content])
                        if tab[0] == "备注" or tab[0] == "温馨提示":
                            end_flag = True

            for i in range(len(data)):
                if data[i][0] == "":
                    data[i - 1][1] += data[i][1]
            return [x for x in data if x[0] != ""]


if __name__ == '__main__':
    data = parse_pdf("d://cars/pdf/1658998940705647_宋PRO DM-i 用户手册 202203版 2022.07.25.pdf")
    print(data)
