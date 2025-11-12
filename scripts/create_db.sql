-- 							 MỤC TIÊU:
-- ==================================================================
-- 1. TẠO DATABASE NẾU CHƯA TỒN TẠI
-- ===================================================================

-- Xóa database nếu tồn tại
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_database WHERE datname = 'house_price'
    ) THEN
        -- Ngắt tất cả kết nối tới database
        PERFORM pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = 'house_price';

        -- Drop database
        EXECUTE 'DROP DATABASE house_price';
    END IF;
END $$;


-- Tạo database mới
CREATE DATABASE house_price
    WITH ENCODING 'UTF8';