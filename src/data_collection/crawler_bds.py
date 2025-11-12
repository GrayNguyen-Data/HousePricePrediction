import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import random
import time

# Cài đặt: pip install undetected-chromedriver

options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options)

try:
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
    
    for infor in (full_infor[1:3]):
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
        title = address = area = floors = furniture = bedrooms = bathrooms = price = price_m2 = None

        # Lấy title
        title_tag = detail_soup.find('h1', class_='re__pr-title pr-title js__pr-title')
        if title_tag:
            title = title_tag.text.strip()

        # Lấy address
        address_tag = detail_soup.find('span', class_="re__pr-short-description js__pr-address")
        if address_tag:
            address = address_tag.text.strip()

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
                area = value
            elif label == "Số tầng":
                floors = value
            elif label == "Nội thất":
                furniture = value
            elif label == "Số phòng ngủ":
                bedrooms = value
            elif label == "Số phòng tắm, vệ sinh":
                bathrooms = value
            elif label == "Khoảng giá":
                price = value
                ext_tag = item.find('span', class_='ext')
                if ext_tag:
                    price_m2 = ext_tag.text.strip()

        # In kết quả
        print(f"Title: {title}")
        print(f"Address: {address}")
        print(f"Area: {area}")
        print(f"Floors: {floors}")
        print(f"Furniture: {furniture}")
        print(f"Bedrooms: {bedrooms}")
        print(f"Bathrooms: {bathrooms}")
        print(f"Price: {price}")
        print(f"Price per m2: {price_m2}")
        print(f"Link: {href}\n")

finally:
    driver.quit()