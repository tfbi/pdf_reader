import json
import os.path

from byd_request import *
from car_maintenance_parse import CarMaintenanceParse
from consts import const
import csv
from copy import deepcopy


def parse_list(url):
    print("准备向商城服务器请求汽车用户手册地址信息.....")
    content = Request(url).get()
    resp_json = json.loads(content.decode("utf-8"))
    print("完成请求，所有汽车用户手册信息如下：" + str(resp_json))
    info_list = []
    if resp_json['status'] == "200":
        data = resp_json['data']
        car_item = dict()
        for info in data:
            car_item['cate_name'] = info['cate_name']
            car_item['cate_id'] = info['cate_id']
            for car in info['goods']:
                car_item['car_id'] = car['id']
                car_item['car_title'] = car['title']
                car_item['car_label'] = car['label']
                car_item['car_label_id'] = car['label_id']
                car_item['download_url'] = car['downloadUrl']
                info_list.append(deepcopy(car_item))
    else:
        raise IOError("接口问题，文件列表获取失败")
    return info_list


def init():
    # 准备存储目录
    if not os.path.exists(const.LOCAL_ZIP_DIR):
        os.makedirs(const.LOCAL_ZIP_DIR)
    if not os.path.exists(const.LOCAL_PDF_DIR):
        os.makedirs(const.LOCAL_PDF_DIR)
    if not os.path.exists(const.CSV_FILE_DIR):
        os.makedirs(const.CSV_FILE_DIR)
    if os.path.exists(const.CSV_FILE_PATH):
        os.remove(const.CSV_FILE_PATH)
    headers = ["car_id", "car_name", "cate_name", "car_label", "mt_type", "mt_content"]
    # 准备csv文件
    with open(const.CSV_FILE_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)


if __name__ == '__main__':
    init()
    start_url = 'https://mall.bydauto.com.cn/api/handbook/list'
    error_pdf_name = []
    info_list = parse_list(start_url)
    for item in info_list:
        car_parse = CarMaintenanceParse(item)
        try:
            car_parse.start_job()
        except Exception as e:
            print(e)
            error_pdf_name.append(car_parse.pdf_file_name)
    print(error_pdf_name)
