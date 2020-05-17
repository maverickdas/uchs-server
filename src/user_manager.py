import math


def insert_guardians(cursor, user_id, guardian_list):
    guardian_query_str = [
        f"guardian_{i}" for i in range(1,
                                       len(guardian_list) + 1)
    ]
    guardian_query_str = ",".join(guardian_query_str)
    guardian_form_str = [f"'{g}'" for g in guardian_list]
    guardian_form_str = ",".join(guardian_form_str)
    query = """
    INSERT INTO uchs_db.user_emergency_contacts_registered
    (user_id , {}) VALUES ('{}', {});
    """.format(guardian_query_str, user_id, guardian_form_str)
    try:
        cursor.execute(query)
        return True
    except Exception:
        raise


def update_guardians(cursor, user_id, guardian_list):
    select_query = """
    SELECT * FROM uchs_db.user_emergency_contacts_registered
    WHERE user_id = '{}';
    """.format(user_id)
    cursor.execute(select_query)
    num_guardians = len([x for x in cursor.fetchone() if x]) - 1
    num_updates = len(guardian_list)
    for i in range(num_guardians - num_updates):
        guardian_list.append('Default')
    guardian_query_str = [
        f"guardian_{i+1} = '{g}'" for i, g in enumerate(guardian_list)
    ]
    guardian_query_str = ",".join(guardian_query_str)
    query = """
    UPDATE uchs_db.user_emergency_contacts_registered
    SET {} WHERE user_id = '{}';
    """.format(guardian_query_str, user_id)
    try:
        cursor.execute(query)
        return True
    except Exception:
        raise


def check_uid_exists(cursor, client_id, utype="user"):
    if "help" in utype:
        query = """
        SELECT COUNT(helpline_id) FROM uchs_db.helpline_tbl
        WHERE helpline_id = '{}';
        """.format(client_id)
    elif "user" in utype:
        query = """
        SELECT COUNT(user_id) FROM uchs_db.user_tbl
        WHERE user_id = '{}';
        """.format(client_id)
    cursor.execute(query)
    cnt = cursor.fetchone()[0]
    if cnt == 0:
        return False
    return True


def register_user(cursor, uid, passw, fname, lname, age, ccode, phone, specz):
    query = """
        INSERT INTO uchs_db.user_tbl
        (user_id, user_first_name, user_last_name, age, user_phone_number_1, user_country_code, user_specialization, password)
        VALUES('{}', '{}', '{}', {}, {}, {}, '{}', AES_ENCRYPT('{}', UNHEX(SHA2('{}',512))));
        """.format(uid, fname, lname, age, phone, ccode, specz, passw, passw)
    cursor.execute(query)


def register_helpline(cursor, hid, passw, hname, ccode, phone, specz, location):
    latt, longt = [round(math.radians(float(x.strip())), 6) for x in location.split(",")]
    loc_check_query = """
    SELECT location_id FROM uchs_db.location_tbl ult
    WHERE ult.latitude = {} AND ult.longitude = {}
    """.format(latt, longt)
    cursor.execute(loc_check_query)
    results = cursor.fetchone()
    if results:
        loc_id = results[0]
    else:
        loc_ins_query = """
        INSERT INTO uchs_db.location_tbl (latitude, longitude)
        VALUES ({}, {});
        """.format(latt, longt)
        cursor.execute(loc_ins_query)
        loc_id = cursor.lastrowid
    query = """
        INSERT INTO uchs_db.helpline_tbl
        (helpline_id, helpline_name, helpline_phone_number_1, helpline_country_code, helpline_type, password, helpline_location_id)
        VALUES('{}', '{}', {}, {}, '{}', AES_ENCRYPT('{}', UNHEX(SHA2('{}',512))), {});
        """.format(hid, hname, phone, ccode, specz, passw, passw, loc_id)
    cursor.execute(query)



def login_client(cursor, client_id, client_passw, utype="user"):
    if "user" in utype:
        query = """
        select COUNT(AES_DECRYPT(ut.password , UNHEX(SHA2('{}',512))))
        from uchs_db.user_tbl ut where ut.user_id ='{}';
        """.format(client_passw, client_id)
    elif "help" in utype:
        query = """
        select COUNT(AES_DECRYPT(ht.password , UNHEX(SHA2('{}',512))))
        from uchs_db.helpline_tbl ht where ht.helpline_id ='{}';
        """.format(client_passw, client_id)
    print(query)
    cursor.execute(query)
    cnt = cursor.fetchone()[0]
    if cnt:
        return True
    return False


