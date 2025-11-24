import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import random
import time
from database.load_data_layer_bronze import load_data_to_bronze_layer


def crawler_and_load_data(max_pages=200):
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")

    with uc.Chrome(options=options) as driver:
        base_url = 'https://batdongsan.com.vn/ban-nha-rieng-tp-hcm'
        for page in range(179, max_pages + 1):
            # Tạo URL theo trang
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}/p{page}"

            print(f"\n🌐 Đang cào trang {page}: {url}")
            driver.get(url)
            time.sleep(random.uniform(8, 12))

            # Scroll human-like
            for _ in range(200):
                driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(random.uniform(0.5, 1.2))

            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            links = soup.find_all('a', class_='js__product-link-for-product-id')

            print(f"Tìm thấy {len(links)} tin ở trang {page}")

            # Cào từng link chi tiết
            for infor in links:
                href = "https://batdongsan.com.vn" + infor.get('href', '')
                try:
                    driver.get(href)
                    time.sleep(random.uniform(15, 18))
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
                    time.sleep(random.uniform(1, 2))

                    detail_html = driver.page_source
                    detail_soup = BeautifulSoup(detail_html, 'lxml')

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

                    # Các thuộc tính khác
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

                    # Giá
                    prices = detail_soup.find_all('div', class_='re__pr-short-info-item js__pr-short-info-item')
                    for item in prices:
                        label_tag = item.find('span', class_='title')
                        value_tag = item.find('span', class_='value')
                        ext_tag = item.find('span', class_='ext')
                        if label_tag and label_tag.text.strip() == "Khoảng giá":
                            if value_tag:
                                data['price'] = value_tag.text.strip()
                            if ext_tag:
                                data['price_m2'] = ext_tag.text.strip()

                    # Ngày đăng
                    date = detail_soup.find_all('div', class_='re__pr-short-info-item js__pr-config-item')
                    for item in date:
                        label_tag = item.find('span', class_='title')
                        value_tag = item.find('span', class_='value')
                        if label_tag and label_tag.text.strip() == "Ngày đăng":
                            if value_tag:
                                data['posted_date'] = value_tag.text.strip()

                    load_data_to_bronze_layer(data)
                    print(f"Đã lưu dữ liệu cho {href}")

                except Exception as e:
                    print(f"Lỗi khi xử lý {href}: {e}")
            
            # Nghỉ 10–15s giữa các trang để tránh bị block
            time.sleep(random.uniform(10, 15))
