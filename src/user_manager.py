import math

from utils import byte_to_int


def get_guardians(cursor, user_id, is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    guardian_query = """
    SELECT * FROM {}.user_emergency_contacts_registered
    WHERE user_id = '{}';
    """.format(db_name, user_id)
    cursor.execute(guardian_query)
    results = cursor.fetchone()
    assert results, f"User '{user_id}' entry does not exist in guardians table!"
    guardian_list = [x for x in results[1:] if x is not None]
    return True, guardian_list


def insert_guardians(cursor, user_id, guardian_list, is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    guardian_query_str = [
        f"guardian_{i}" for i in range(1,
                                       len(guardian_list) + 1)
    ]
    guardian_query_str = ",".join(guardian_query_str)
    guardian_form_str = [f"'{g}'" for g in guardian_list]
    guardian_form_str = ",".join(guardian_form_str)
    query = """
    INSERT INTO {}.user_emergency_contacts_registered
    (user_id , {}) VALUES ('{}', {});
    """.format(db_name, guardian_query_str, user_id, guardian_form_str)
    try:
        cursor.execute(query)
        return True
    except Exception:
        raise


def update_guardians(cursor, user_id, guardian_list, is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    select_query = """
    SELECT * FROM {}.user_emergency_contacts_registered
    WHERE user_id = '{}';
    """.format(db_name, user_id)
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
    UPDATE {}.user_emergency_contacts_registered
    SET {} WHERE user_id = '{}';
    """.format(db_name, guardian_query_str, user_id)
    try:
        cursor.execute(query)
        return True
    except Exception:
        raise


def check_uid_exists(cursor, client_id, utype="user", is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    if "help" in utype:
        query = """
        SELECT COUNT(helpline_id) FROM {}.helpline_tbl
        WHERE helpline_id = '{}';
        """.format(db_name, client_id)
    elif "user" in utype:
        query = """
        SELECT COUNT(user_id) FROM {}.user_tbl
        WHERE user_id = '{}';
        """.format(db_name, client_id)
    cursor.execute(query)
    cnt = cursor.fetchone()[0]
    if cnt == 0:
        return False
    return True


def check_pending(cursor, client_id, is_user=True, is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    if is_user:
        check_query = """
        SELECT pending FROM {}.user_tbl
        WHERE user_id = '{}'
        """.format(db_name, client_id)
    else:
        check_query = """
        SELECT pending FROM {}.helpline_tbl
        WHERE helpline_id = '{}'
        """.format(db_name, client_id)
    cursor.execute(check_query)
    pending = cursor.fetchone()[0]
    print(f"\t{pending} notifications for {client_id}")
    if pending > 0:
        return True
    return False


def get_pending_alerts(cursor, client_id, is_user=True, is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    if is_user:
        query = """
        SELECT alarm_id FROM {}.user_alert_status
        WHERE user_id = '{}' AND status = 0; 
        """.format(db_name, client_id)
    else:
        query = """
        SELECT alarm_id FROM {}.helpline_alert_status
        WHERE helpline_id = '{}' AND status = 0; 
        """.format(db_name, client_id)
    cursor.execute(query)
    results = cursor.fetchall()
    try:
        return [x[0] for x in results]
    except Exception:
        return []


def register_user(cursor, uid, passw, fname, lname, age,
                  ccode, phone, specz, is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    query = """
        INSERT INTO {}.user_tbl
        (user_id, user_first_name, user_last_name, age, user_phone_number_1, user_country_code, user_specialization, password)
        VALUES('{}', '{}', '{}', {}, {}, {}, '{}', AES_ENCRYPT('{}', UNHEX(SHA2('{}',512))));
        """.format(db_name, uid, fname, lname, age, phone, ccode, specz, passw,
                   passw)
    cursor.execute(query)
    # 0,0 as live location for new-users
    live_loc_query = """
    INSERT INTO {}.user_live_location
    (user_id, latitude, longitude)
    VALUES ('{}', {}, {})
    """.format(db_name, uid, 0, 0)
    cursor.execute(live_loc_query)
    # null guardians for new-users
    guardian_query = """
    INSERT INTO {}.user_emergency_contacts_registered (user_id) VALUES ('{}')
    """.format(db_name, uid)
    cursor.execute(guardian_query)


def register_helpline(cursor, hid, passw, hname, ccode,
                      phone, specz, location, is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    latt, longt = [
        round(math.radians(float(x.strip())), 6) for x in location.split(",")
    ]
    loc_check_query = """
    SELECT location_id FROM {}.location_tbl ult
    WHERE ult.latitude = {} AND ult.longitude = {}
    """.format(db_name, latt, longt)
    cursor.execute(loc_check_query)
    results = cursor.fetchone()
    if results:
        loc_id = results[0]
    else:
        loc_ins_query = """
        INSERT INTO {}.location_tbl (latitude, longitude)
        VALUES ({}, {});
        """.format(db_name, latt, longt)
        cursor.execute(loc_ins_query)
        loc_id = cursor.lastrowid
    query = """
        INSERT INTO {}.helpline_tbl
        (helpline_id, helpline_name, helpline_phone_number_1, helpline_country_code, helpline_type, password, helpline_location_id)
        VALUES('{}', '{}', {}, {}, '{}', AES_ENCRYPT('{}', UNHEX(SHA2('{}',512))), {});
        """.format(db_name, hid, hname, phone, ccode, specz, passw, passw,
                   loc_id)
    cursor.execute(query)


def login_client(cursor, client_id, client_passw, utype="user", is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    if "user" in utype:
        login_check_query = """
        SELECT login_status FROM {}.user_tbl ut
        WHERE ut.user_id = '{}'
        """.format(db_name, client_id)
        pass_check_query = """
        select COUNT(AES_DECRYPT(ut.password , UNHEX(SHA2('{}',512))))
        from {}.user_tbl ut where ut.user_id ='{}';
        """.format(client_passw, db_name, client_id)
        login_status_update = """
        UPDATE {}.user_tbl SET login_status = 1
        WHERE user_id = '{}'
        """.format(db_name, client_id)
    elif "help" in utype:
        login_check_query = """
        SELECT login_status FROM {}.helpline_tbl ut
        WHERE ut.helpline_id = '{}'
        """.format(db_name, client_id)
        pass_check_query = """
        select COUNT(AES_DECRYPT(ht.password , UNHEX(SHA2('{}',512))))
        from {}.helpline_tbl ht where ht.helpline_id ='{}';
        """.format(client_passw, db_name, client_id)
        login_status_update = """
        UPDATE {}.helpline_tbl SET login_status = 1
        WHERE helpline_id = '{}'
        """.format(db_name, client_id)
    cursor.execute(login_check_query)
    result = cursor.fetchone()
    if not result:
        return False, f"'{client_id}' is unregistered!"
    is_loggedin = byte_to_int(result[0])
    if is_loggedin:
        return False, f"'{client_id}' has already logged in!"
    cursor.execute(pass_check_query)
    cnt = cursor.fetchone()[0]
    if not cnt:
        return False, f"'{client_id}' password is incorrect!"
    cursor.execute(login_status_update)
    return True, f"Login successful!"


def logout_client(cursor, client_id, utype="user", is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    if "user" in utype:
        login_check_query = """
        SELECT login_status FROM {}.user_tbl ut
        WHERE ut.user_id = '{}'
        """.format(db_name, client_id)
        login_status_update = """
        UPDATE {}.user_tbl SET login_status = 0
        WHERE user_id = '{}'
        """.format(db_name, client_id)
    elif "help" in utype:
        login_check_query = """
        SELECT login_status FROM {}.helpline_tbl ut
        WHERE ut.helpline_id = '{}'
        """.format(db_name, client_id)
        login_status_update = """
        UPDATE {}.helpline_tbl SET login_status = 0
        WHERE helpline_id = '{}'
        """.format(db_name, client_id)
    cursor.execute(login_check_query)
    result = cursor.fetchone()
    if not result:
        return False, f"'{client_id}' is unregistered!"
    is_loggedin = byte_to_int(result[0])
    if not is_loggedin:
        print(f"--ALERT: {utype} STACKED LOGOUT by '{client_id}'--")
        return False, f"Stacked logouts from '{client_id}'!"
    cursor.execute(login_status_update)
    return True, "Logout successful!"


def update_live_location(cursor, user_id, location, is_alt=False):
    db_name = "uchs_test" if is_alt else "uchs_db"
    latt, longt = [
        math.radians(float(x.strip())) for x in location.split(",")
    ]
    query = """
    UPDATE {}.user_live_location
    SET latitude={}, longitude={}, `timestamp`=CURRENT_TIMESTAMP
    WHERE user_id='{}';
    """.format(db_name, latt, longt, user_id)
    cursor.execute(query)
