import os.path
import zipfile
import pdfplumber
from byd_request import *
from consts import const
import re
import csv
from unrar import rarfile


class CarMaintenanceParse:
    def __init__(self, car_info):
        self.car_info = car_info
        self.url = car_info['download_url']
        self.compress_file_name = self.url.split("/")[-1]
        self.pdf_file_name = self.url.split("/")[-1][:-4] + ".pdf"
        self.compress_file_path = const.LOCAL_ZIP_DIR + "/" + self.compress_file_name
        self.pdf_file_path = const.LOCAL_PDF_DIR + "/" + self.pdf_file_name
        self.car_id = car_info['car_id']

    def download_file(self):
        print(self.compress_file_name + ":准备下载文件")
        try:
            content = Request(self.url).get()
            with open(self.compress_file_path, "wb") as f:
                f.write(content)
        except Exception as error:
            print(error)
            return False

        if os.path.exists(self.compress_file_path):
            print(self.compress_file_name + ":文件下载完成")
            return True
        else:
            return False

    def unrar2pdf(self):
        print(self.compress_file_name + "：开始解压")
        try:
            zf = rarfile.RarFile(self.compress_file_path, 'r')
            max_file = ["", 0]
            for x in zf.namelist():
                if ".pdf" in x:
                    pdf_path = zf.extract(x, const.LOCAL_PDF_DIR)
                    if os.stat(pdf_path).st_size > max_file[1]:
                        max_file[0] = pdf_path
                        max_file[1] = os.stat(pdf_path).st_size
            os.rename(max_file[0], self.pdf_file_path)
        except Exception as error:
            print(error)
            return False

        if os.path.exists(self.pdf_file_path):
            print(self.compress_file_name + ":文件解压完成")
            return True
        else:
            return False

    def unzip2pdf(self):
        print(self.compress_file_name + "：开始解压")
        try:
            zf = zipfile.ZipFile(self.compress_file_path, 'r')
            max_file = ["", 0]
            for x in zf.namelist():
                if ".pdf" in x:
                    pdf_path = zf.extract(x, const.LOCAL_PDF_DIR)
                    if os.stat(pdf_path).st_size > max_file[1]:
                        max_file[0] = pdf_path
                        max_file[1] = os.stat(pdf_path).st_size
            os.rename(max_file[0], self.pdf_file_path)
        except Exception as error:
            print(error)
            return False

        if os.path.exists(self.pdf_file_path):
            print(self.compress_file_name + ":文件解压完成")
            return True
        else:
            return False

    def parse_pdf(self):
        with pdfplumber.open(self.pdf_file_path) as pdf:
            re1 = re.compile(r".*?保养.*?(\d+)")
            num_list = []
            for page in pdf.pages[4:8]:
                text = page.extract_text()
                ret = re1.findall(text)
                if len(ret) > 0:
                    for x in ret:
                        if int(x) >= len(pdf.pages) // 2:
                            num_list.append(int(x))
                    break
            print(num_list)
            if len(num_list) > 0:
                tables = []
                table_settings = {}
                if self.car_id in [10, 11, 12, 15, 91, 31, 90, 29, 30]:
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
                                        continue
                                    title += x.replace("\n", "")
                                if "I" in title or "I" in content:
                                    continue
                                data.append([title, content])
                            if tab[0] == "备注" or tab[0] == "温馨提示":
                                end_flag = True

                for i in range(len(data)):
                    if data[i][0] == "":
                        data[i - 1][1] += data[i][1]
                return [x for x in data if x[0] != ""]

    def save_csv(self, data):
        with open(const.CSV_FILE_PATH, "a+", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            rows = [(self.car_info['car_id'],
                     self.car_info['car_title'],
                     self.car_info['cate_name'],
                     self.car_info['car_label']
                     , x[0], x[1]) for x in data]
            writer.writerows(rows)
        print(self.pdf_file_name + " 解析数据写入csv文件完成")

    def start_job(self):
        # 1. 根据url地址去下载对应的用户手册zip文件
        if not os.path.exists(self.compress_file_path):
            download_ret = self.download_file()
            if not download_ret:
                raise IOError(self.compress_file_name + "文件下载失败")
        else:
            print(self.compress_file_name + "文件已存在，无需下载")
        # 2. 解压zip文件，并处理文件名乱码问题
        if not os.path.exists(self.pdf_file_path):
            if ".zip" in self.compress_file_name:
                unzip_ret = self.unzip2pdf()
                if not unzip_ret:
                    raise TypeError(self.compress_file_name + "文件解压失败")
            else:
                unrar_ret = self.unrar2pdf()
                if not unrar_ret:
                    raise TypeError(self.compress_file_name + "文件解压失败")
        else:
            print(self.pdf_file_name + "文件已存在，无需解压")

        # 3.解析pdf文件中的维保数据
        data = self.parse_pdf()
        car_dict = {"car_id": self.car_info['car_id'],
                    "car_name": self.car_info['car_title'],
                    "car_label": self.car_info['car_label'],
                    "cate_name": self.car_info['cate_name'],
                    "maintenances": data
                    }
        # print("解析后的json数据如下：")
        # print(car_dict)
        # 4. 追加方式写入csv
        if data:
            self.save_csv(data)
