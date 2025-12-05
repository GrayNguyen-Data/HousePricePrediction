from database.connect_db import connect

def load_data_to_bronze_layer(data):
    conn, cur = connect()
    query = """
        INSERT INTO bronze.raw_data (
            title,
            address,
            area,
            floors,
            furniture,
            bedrooms,
            bathrooms,
            price,
            price_m2,
            posted_date,
            link
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT (link) DO NOTHING;
    """

    cur.execute(query, (
        data['title'],
        data['address'],
        data['area'],
        data['floors'],
        data['furniture'],
        data['bedrooms'],
        data['bathrooms'],
        data['price'],
        data['price_m2'],
        data['posted_date'],
        data['link']
    ))
    conn.commit()

    # 🔄 Reset sequence id để đồng bộ với giá trị lớn nhất hiện có
    reset_seq = """
        SELECT setval(
            pg_get_serial_sequence('bronze.raw_data', 'id'),
            COALESCE((SELECT MAX(id) FROM bronze.raw_data), 1),
            true
        );
    """
    cur.execute(reset_seq)
    conn.commit()

    cur.close()
    conn.close()
