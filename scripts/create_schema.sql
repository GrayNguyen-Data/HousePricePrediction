
-- 							 MỤC TIÊU:
-- ==================================================================

-- 2. TẠO CÁC SCHEMA THEO KIẾN TRÚC MEDALLION
-- Mục đích phân lớp dữ liệu theo kiến trúc 3 tầng 
-- bronze: lưu trữ dữ liệu thô (raw data)
-- silver: lưu dữu liệu đã qua xử lý (cleaned and transformed)
-- gold: lưu dữ liệu sẵn sàng cho phân tích/mô hình(anylytics-ready).

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;