CREATE TABLE fact_sales (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Khóa chính tự tăng
    itemId TEXT NOT NULL,                      -- Khóa tham chiếu đến sản phẩm
    platform TEXT NOT NULL,                    -- Khóa tham chiếu đến nền tảng
    salePrice REAL NOT NULL,                   -- Giá bán (metric)
    scraped_timestamp DATETIME NOT NULL,       -- Thời gian thu thập dữ liệu
    total_reviews INTEGER,                     -- Tổng số đánh giá (từ bảng review)
    rating REAL,                               -- Đánh giá trung bình (từ bảng review)
    FOREIGN KEY (itemId) REFERENCES pdp(product_id),
    FOREIGN KEY (platform) REFERENCES pdp(platform)
);

INSERT INTO fact_sales (itemId, platform, salePrice, scraped_timestamp, total_reviews, rating)
SELECT 
    h.itemId,
    h.platform,
    h.salePrice,
    h.scraped_timestamp,
    r.total_reviews,
    p.rating
FROM 
    historical h
LEFT JOIN 
    pdp p ON h.itemId = p.product_id AND h.platform = p.platform
LEFT JOIN 
    review r ON h.itemId = r.product_id AND h.platform = r.platform;
