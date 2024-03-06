import requests
import xml.etree.ElementTree as et
import csv
import cv2
from pyzbar.pyzbar import decode

# 本の情報を保存するファイルのパス
FILE_PATH = r'/Users/tony/Desktop/temp.csv'

# パソコンのカメラを使ってisbnコードを読み取る
def cam_capture():
    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    barcodes = []

    while cap.isOpened():
        ret, frame = cap.read()

        if ret:
            d = decode(frame)

            if d:
                for barcode in d:
                    barcode_data = barcode.data.decode('utf-8')

                    if is_isbn(barcode_data):

                        if barcode_data not in barcodes:
                            try:
                                barcodes.append(barcode_data)

                                font_color = (0, 0, 255)
                                result = fetch_book_data(barcode_data)
                                

                                with open(FILE_PATH, mode='a', encoding='shift-jis', newline='') as buf:
                                    writer = csv.writer(buf)
                                    writer.writerow(list(result))

                            except Exception as e:
                                print(f"Error occurred while fetching book data: {e}")
                                font_color = (0, 0, 0)  # Change the font color to indicate the error
                        else:
                            font_color = (0, 154, 87)

                        x, y, w, h = barcode.rect
                        cv2.rectangle(frame, (x, y), (x + w, y + h), font_color, 2)
                        frame = cv2.putText(frame, barcode_data, (x, y - 10), 
                                            font, .5, font_color, 2, cv2.LINE_AA)

        cv2.imshow('isbnscanner: Press Q to Exit', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

# スキャンした本の情報をウェブで獲得する
def fetch_book_data(isbn):
    endpoint = 'https://iss.ndl.go.jp/api/sru'
    params = {'operation': 'searchRetrieve',
              'query': f'isbn="{isbn}"',
              'recordPacking': 'xml'}

    res = requests.get(endpoint, params=params)

    root = et.fromstring(res.text)
    ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
    title_element = root.find('.//dc:title', ns)
    creator_element = root.find('.//dc:creator', ns)
    publisher_element = root.find('.//dc:publisher', ns)
    subject_element = root.find('.//dc:subject', ns)

    title = title_element.text.encode('utf-8').decode() if title_element is not None else ""
    creator = creator_element.text.encode('utf-8').decode() if creator_element is not None else ""
    publisher = publisher_element.text.encode('utf-8').decode() if publisher_element is not None else ""
    subject = subject_element.text.encode('utf-8').decode() if subject_element is not None else ""

    return isbn, title, creator, publisher, subject

# スキャンしたコードはisbnコードかどうかを確認する
def is_isbn(code):
    return len(code) == 13 and code[:3] == '978'

# プログラムを実行する
cam_capture()