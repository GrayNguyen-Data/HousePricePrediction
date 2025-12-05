import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import random
import time
from database.load_data_layer_bronze import load_data_to_bronze_layer
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


def crawler_and_load_data(max_pages=70):
    # Sử dụng try...finally để đảm bảo driver được đóng (khắc phục lỗi WinError 6)
    driver = None 
    try:
        options = uc.ChromeOptions()
        # Vẫn giữ tùy chọn chống bot cơ bản
        options.add_argument("--disable-blink-features=AutomationControlled") 
        # Tùy chọn đề xuất: Chạy ẩn (headless) để tăng tốc và giảm rủi ro bị block
        # options.add_argument('--headless') 

        driver = uc.Chrome(options=options)
        # Đặt Implicit Wait để giúp driver tìm kiếm phần tử nhanh hơn (tối đa 10 giây)
        driver.implicitly_wait(10)
        
        base_url = 'https://batdongsan.com.vn/ban-nha-rieng-tp-hcm'
        
        for page in range(43, max_pages + 1):
            # Tối ưu logic tạo URL: Đơn giản và chính xác
            url = f"{base_url}/p{page}" if page > 1 else base_url

            print(f"\n🌐 Đang cào trang {page}: {url}")
            driver.get(url)
            
            # Tối ưu: Thay time.sleep dài bằng Explicit Wait
            try:
                # Chờ đợi ít nhất một link tin chi tiết xuất hiện
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'js__product-link-for-product-id'))
                )
            except TimeoutException:
                print(f"❌ Timeout! Không tìm thấy tin nào ở trang {page}. Có thể đã bị block hoặc hết trang.")
                # Nếu hết trang/bị block, nên thoát vòng lặp ngoài
                break

            # Scroll human-like (tăng tốc độ, giảm số lần scroll)
            for _ in range(5):
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(random.uniform(0.3, 0.8))

            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            links = soup.find_all('a', class_='js__product-link-for-product-id')

            print(f"Tìm thấy {len(links)} tin ở trang {page}")

            # Cào từng link chi tiết
            for infor in links:
                href = "https://batdongsan.com.vn" + infor.get('href', '')
                try:
                    driver.get(href)
                    
                    # Tối ưu: Explicit Wait cho tiêu đề tin chi tiết
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 're__pr-title'))
                    )
                    
                    # Scroll nhẹ để tải nội dung động (giảm thời gian nghỉ)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
                    time.sleep(random.uniform(1, 1.5))

                    detail_html = driver.page_source
                    detail_soup = BeautifulSoup(detail_html, 'lxml')

                    # ----------------- LOGIC TRÍCH XUẤT DỮ LIỆU -----------------
                    # ... (Logic trích xuất dữ liệu giữ nguyên, nó đã đúng) ...
                    
                    data = {
                        'title': None, 'address': None, 'area': None, 'floors': None,
                        'furniture': None, 'bedrooms': None, 'bathrooms': None,
                        'price': None, 'price_m2': None, 'posted_date': None, 'link': href
                    }
                    
                    # Lấy title
                    title_tag = detail_soup.find('h1', class_='re__pr-title pr-title js__pr-title')
                    if title_tag:
                        data['title'] = title_tag.text.strip()

                    # Lấy address
                    address_tag = detail_soup.find('span', class_="re__pr-short-description js__pr-address")
                    if address_tag:
                        data['address'] = address_tag.text.strip()
                        
                    # Các thuộc tính khác (Diện tích, Số tầng,...)
                    items = detail_soup.find_all('div', class_='re__pr-specs-content-item')
                    for item in items:
                        label_tag = item.find('span', class_='re__pr-specs-content-item-title')
                        value_tag = item.find('span', class_='re__pr-specs-content-item-value')
                        if not label_tag or not value_tag: continue
                        label = label_tag.text.strip()
                        value = value_tag.text.strip()
                        if label == "Diện tích": data['area'] = value
                        elif label == "Số tầng": data['floors'] = value
                        elif label == "Nội thất": data['furniture'] = value
                        elif label == "Số phòng ngủ": data['bedrooms'] = value
                        elif label == "Số phòng tắm, vệ sinh": data['bathrooms'] = value

                    # Giá
                    prices = detail_soup.find_all('div', class_='re__pr-short-info-item js__pr-short-info-item')
                    for item in prices:
                        label_tag = item.find('span', class_='title')
                        value_tag = item.find('span', class_='value')
                        ext_tag = item.find('span', class_='ext')
                        if label_tag and label_tag.text.strip() == "Khoảng giá":
                            if value_tag: data['price'] = value_tag.text.strip()
                            if ext_tag: data['price_m2'] = ext_tag.text.strip()

                    # Ngày đăng
                    date = detail_soup.find_all('div', class_='re__pr-short-info-item js__pr-config-item')
                    for item in date:
                        label_tag = item.find('span', class_='title')
                        value_tag = item.find('span', class_='value')
                        if label_tag and label_tag.text.strip() == "Ngày đăng":
                            if value_tag: data['posted_date'] = value_tag.text.strip()

                    # 6. LƯU DỮ LIỆU
                    load_data_to_bronze_layer(data)
                    print(f"✅ Đã lưu dữ liệu cho {data.get('title', href)}")

                except Exception as e:
                    print(f"❌ Lỗi khi xử lý {href}: {e}")
                
                # Tối ưu: Nghỉ ngắn và ngẫu nhiên giữa các tin chi tiết (giảm từ 15-18s xuống 3-5s)
                time.sleep(random.uniform(3, 5)) 
            
            # Tối ưu: Nghỉ giữa các trang (giảm từ 10-15s xuống 5-10s)
            time.sleep(random.uniform(5, 10))
            
    except WebDriverException as overall_e:
        # Bắt các lỗi liên quan đến driver (như SessionNotCreatedException, ConnectionRefused)
        print(f"❌ Lỗi nghiêm trọng của WebDriver (Kiểm tra phiên bản Chrome/Driver): {overall_e}")

    except Exception as overall_e:
        print(f"❌ Lỗi chung trong quá trình cào dữ liệu: {overall_e}")

    finally:
        # 7. FIX WINERROR 6: Đóng driver an toàn
        if driver:
            try:
                driver.quit()
                print("Đã đóng Driver an toàn.")
            except Exception as close_error:
                # Ngoại lệ bị bỏ qua WinError 6 thường được bắt ở đây
                print(f"Cảnh báo: Lỗi khi đóng Driver (đã được bỏ qua): {close_error}")