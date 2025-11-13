
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import random
import time
from loads.load_data_layer_bronze import load_data_to_bronze_layer

def crawler_and_load_data():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")

    with uc.Chrome(options=options) as driver:
        URL = 'https://batdongsan.com.vn/ban-nha-rieng-tp-hcm'
        driver.get(URL)
        time.sleep(random.uniform(8, 12))
        
        # Scroll human-like
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(random.uniform(0.5, 1.2))

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        full_infor = soup.find_all('a', class_='js__product-link-for-product-id')
        
        for infor in (full_infor[:2]):
            href = "https://batdongsan.com.vn" + infor.get('href', '')

            # Truy cập trang chi tiết với random delay
            driver.get(href)
            time.sleep(random.uniform(15, 18))  # Tăng thời gian chờ
            
            # Scroll một chút để giống người dùng thật
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(random.uniform(1, 2))

            detail_html = driver.page_source
            detail_soup = BeautifulSoup(detail_html, 'lxml')

            # Khởi tạo các giá trị null trước bởi vì có các thuộc tính có thể không tồn tại
            data = {
                'title': None,
                'address': None,
                'area': None,
                'floors': None,
                'furniture': None,
                'bedrooms': None,
                'bathrooms': None,
                'price': None,
                'price_m2': None,
                'posted_date': None,
                'link': href
            }

            # Lấy title
            title_tag = detail_soup.find('h1', class_='re__pr-title pr-title js__pr-title')
            if title_tag:
                data['title'] = title_tag.text.strip()

            # Lấy address
            address_tag = detail_soup.find('span', class_="re__pr-short-description js__pr-address")
            if address_tag:
                data['address'] = address_tag.text.strip()

            # Lấy các thuộc tính khác
            items = detail_soup.find_all('div', class_='re__pr-specs-content-item')
            for item in items:
                label_tag = item.find('span', class_='re__pr-specs-content-item-title')
                value_tag = item.find('span', class_='re__pr-specs-content-item-value')
                
                if not label_tag or not value_tag:
                    continue

                label = label_tag.text.strip()
                value = value_tag.text.strip()

                if label == "Diện tích":
                    data['area'] = value
                elif label == "Số tầng":
                    data['floors'] = value
                elif label == "Nội thất":
                    data['furniture'] = value
                elif label == "Số phòng ngủ":
                    data['bedrooms'] = value
                elif label == "Số phòng tắm, vệ sinh":
                    data['bathrooms'] = value
            prices = detail_soup.find_all('div', class_='re__pr-short-info-item js__pr-short-info-item')

            for item in prices:
                label_tag = item.find('span', class_='title')
                value_tag = item.find('span', class_='value')
                ext_tag = item.find('span', class_='ext')  # giá/m²

                if label_tag and label_tag.text.strip() == "Khoảng giá":
                    if value_tag:
                        data['price'] = value_tag.text.strip()
                    if ext_tag:
                        data['price_m2'] = ext_tag.text.strip()
            date = detail_soup.find_all('div', class_ = 're__pr-short-info-item js__pr-config-item')
            for item in date:
                label_tag = item.find('span', class_='title')
                value_tag = item.find('span', class_='value')
                if label_tag and label_tag.text.strip() == "Ngày đăng":
                    if value_tag:
                        data['posted_date'] = value_tag.text.strip()

            try:
                load_data_to_bronze_layer(data)
                print(f"Data loaded to bronze layer for link: {href}")
            except Exception as e:
                print(f"Error loading data to bronze layer: {e}")