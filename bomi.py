from flask import Flask, render_template, jsonify, request, send_from_directory
from datetime import datetime, timedelta
import pymysql
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from analyzer import SpeechAnalyzer
from llm_handler_with_qa_v2 import LLMHandler
from db_handler import VoiceDBHandler
import uuid

app = Flask(__name__)
CORS(app)
speech_analyzer = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TTS_FOLDER = os.path.join(BASE_DIR, 'tts_outputs')
os.makedirs(TTS_FOLDER, exist_ok=True)

llm_handler = None
voice_db_handler = None
tts_handler = None


# 👇 [여기부터] 이 3줄을 꼭 추가해! (Ngrok 로그인 유지용)
app.secret_key = 'bomi_secret_key'           # 암호화 키 (아무거나 써도 됨)
app.config['SESSION_COOKIE_SAMESITE'] = 'None' # 외부(Ngrok)에서도 허용
app.config['SESSION_COOKIE_SECURE'] = True     # HTTPS에서만 작동하도록 설정
# 👆 [여기까지]


# 데이터베이스 연결 설정
def get_db():
    return pymysql.connect(
        host='192.168.0.31',  # <-- 워크벤치에 넣은 칼리 IP 주소로 수정!
        user='root',
        password='1234', 
        db='care_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )





@app.route('/')
def index():
    return render_template('index.html')






# [수정됨] 깔끔해진 회원가입 API (HTML에서 한글을 보내주므로 변환 불필요)
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()

    try:
        # 비밀번호 해시 암호화
        hashed_password = generate_password_hash(data['guardian']['password'])

        # 1. 보호자 저장
        sql_guardian = """
            INSERT INTO tb_guardian 
            (user_id, password, name, phone, post_num, addr1, addr2, relation_with_senior, voice_collection_approved, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(sql_guardian, (
            data['guardian']['username'],
            hashed_password,
            data['guardian']['name'],
            data['guardian']['phone'],
            data['guardian']['zipcode'],
            data['guardian']['address'],
            data['guardian']['addressDetail'],
            data['senior']['relation'],
            'Y'
        ))
        new_guardian_id = cursor.lastrowid

        # 2. 어르신 저장 (생년월일 조립 & 성별 변환)
        sr = data['senior']
        
        # 생년월일 합치기 (YYYY-MM-DD)
        if 'fullBirthdate' in sr and sr['fullBirthdate']:
            final_birth = sr['fullBirthdate']
        else:
            final_birth = f"{sr.get('birthYear')}-{sr.get('birthMonth').zfill(2)}-{sr.get('birthDay').zfill(2)}"

        # 성별 변환 (영어 -> 한글 DB값)
        final_gender = 'F' if 'female' in sr.get('gender', '') else 'M'

        sql_senior = """
            INSERT INTO tb_senior 
            (name, birthdate, gender, phone, post_num, addr1, addr2, relation_with_guardian, living_type, guardian_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(sql_senior, (
            sr['name'],
            final_birth,
            final_gender,
            sr['phone'],
            sr['zipcode'],
            sr['address'],
            sr['addressDetail'],
            "보호자",
            sr['living'], # HTML에서 '독거','가족'으로 보내주므로 그대로 저장!
            new_guardian_id
        ))
        
        conn.commit()
        return jsonify({"message": "가입 성공", "guardian_id": new_guardian_id})

    except Exception as e:
        conn.rollback()
        print(f"❌ 가입 에러: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# [최종 수정] 로그인 API (기기 목록 조회 기능 추가)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. 보호자 아이디로만 우선 조회
        cursor.execute("SELECT * FROM tb_guardian WHERE user_id = %s", (username,))
        guardian = cursor.fetchone()
        
        # 비밀번호 해시 검증
        if not guardian or not check_password_hash(guardian.get('password', guardian[2] if isinstance(guardian, tuple) else ''), password):
            return jsonify({"error": "로그인 실패"}), 401

        # 딕셔너리 변환 (안전장치)
        if not isinstance(guardian, dict):
            g_dict = {
                'guardian_id': guardian[0], 'name': guardian[1], 'phone': guardian[2],
                'post_num': guardian[3], 'addr1': guardian[4], 'addr2': guardian[5], 'user_id': guardian[9]
            }
        else:
            g_dict = guardian

        # 기본 사용자 정보 구성
        user_data = {
            "username": g_dict['user_id'],
            "name": g_dict['name'],
            "phone": g_dict['phone'],
            "zipcode": g_dict['post_num'],
            "address": g_dict['addr1'],
            "addressDetail": g_dict['addr2'],
            "senior": None,
            "devices": [] # 👈 기기 목록 초기화
        }
        
        # 2. 어르신 조회
        cursor.execute("SELECT * FROM tb_senior WHERE guardian_id = %s", (g_dict['guardian_id'],))
        senior = cursor.fetchone()
        
        if senior:
            if not isinstance(senior, dict):
                 s_dict = {
                     'senior_id': senior[0], # ID가 0번째라고 가정
                     'name': senior[1], 'birthdate': senior[2], 'gender': senior[3], 
                     'phone': senior[4], 'post_num': senior[5], 'addr1': senior[6], 'addr2': senior[7],
                     'living_type': senior[9]
                 }
            else:
                s_dict = senior

            # 생년월일 처리
            birth_str = str(s_dict['birthdate']) 
            b_year, b_month, b_day = birth_str.split('-')

            user_data["senior"] = {
                "name": s_dict['name'],
                "gender": 'female' if s_dict['gender'] == 'F' else 'male',
                "phone": s_dict['phone'],
                "living": s_dict['living_type'],
                "birthYear": b_year,
                "birthMonth": b_month,
                "birthDay": b_day,
                "zipcode": s_dict['post_num'],
                "address": s_dict['addr1'],
                "addressDetail": s_dict['addr2']
            }

            # ==========================================
            # 🌟 [추가됨] 3. 기기 목록 조회
            # ==========================================
            sql_devices = "SELECT * FROM tb_device WHERE senior_id = %s"
            cursor.execute(sql_devices, (s_dict['senior_id'],))
            devices = cursor.fetchall()

            device_list = []
            for d in devices:
                # DB 컬럼명에 맞춰서 프론트엔드 형식으로 변환
                # (add_device에서 device_uid, device_name, location을 썼음)
                d_obj = {
                    'id': f"DEV{d['device_id']}",     # 고유 ID
                    'serial': d['device_uid'],        # 시리얼 번호
                    'name': d['device_name'],         # 기기 이름
                    'location': d['location'],        # 설치 위치
                    'status': 'online'                # 상태 (기본값)
                }
                device_list.append(d_obj)
            
            user_data["devices"] = device_list
            
        return jsonify(user_data)

    except Exception as e:
        print(f"❌ 로그인 에러: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# ==========================================
# 👇 bomi.py 맨 아래에 추가 (활동량 조회 API)
# ==========================================

@app.route('/api/activity-daily', methods=['POST'])
def activity_daily():
    data = request.get_json()
    user_id = data.get('username')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. 사용자의 '모션 센서' ID 찾기 (motion 타입)
        # (복잡한 조인 대신 서브쿼리 활용)
        sql_sensor = """
            SELECT s.sensor_id 
            FROM tb_sensor s
            JOIN tb_device d ON s.device_id = d.device_id
            JOIN tb_senior sn ON d.senior_id = sn.senior_id
            JOIN tb_guardian g ON sn.guardian_id = g.guardian_id
            WHERE g.user_id = %s AND s.sensor_type = 'motion'
            LIMIT 1
        """
        cursor.execute(sql_sensor, (user_id,))
        sensor = cursor.fetchone()
        
        count = 0
        if sensor:
            sensor_id = sensor['sensor_id'] if isinstance(sensor, dict) else sensor[0]
            
            # 2. '오늘' 해당 센서가 감지된 횟수 조회 (tb_sensing 테이블)
            # (만약 tb_sensing 테이블이 없다면 이 부분에서 에러가 날 수 있으니 테이블 확인 필요!)
            sql_count = """
                SELECT COUNT(*) as cnt 
                FROM tb_sensing 
                WHERE sensor_id = %s AND DATE(created_at) = CURDATE()
            """
            cursor.execute(sql_count, (sensor_id,))
            result = cursor.fetchone()
            count = result['cnt'] if isinstance(result, dict) else result[0]
            
        return jsonify({"count": count})
        
    except Exception as e:
        print(f"❌ 활동량 조회 에러: {e}")
        # 에러 나도 0으로 보여주기 (앱이 멈추지 않게)
        return jsonify({"count": 0})
    finally:
        conn.close()
        
        
# ==========================================
# 👇 bomi.py 맨 아래에 추가 (데이터 시뮬레이션 API)
# ==========================================

@app.route('/api/simulate-data', methods=['POST'])
def simulate_data():
    data = request.get_json()
    user_id = data.get('username')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. 사용자의 '모션 센서' 찾기
        sql_sensor = """
            SELECT s.sensor_id 
            FROM tb_sensor s
            JOIN tb_device d ON s.device_id = d.device_id
            JOIN tb_senior sn ON d.senior_id = sn.senior_id
            JOIN tb_guardian g ON sn.guardian_id = g.guardian_id
            WHERE g.user_id = %s AND s.sensor_type = 'motion'
            LIMIT 1
        """
        cursor.execute(sql_sensor, (user_id,))
        sensor = cursor.fetchone()
        
        current_count = 0
        
        if sensor:
            s_id = sensor['sensor_id'] if isinstance(sensor, dict) else sensor[0]
            
            # 2. [핵심] 가짜 데이터(움직임 감지)를 진짜 DB에 저장!
            # (tb_sensing 테이블에 데이터가 쌓여야 횟수가 올라갑니다)
            sql_insert = "INSERT INTO tb_sensing (sensor_id, value, created_at) VALUES (%s, 1, NOW())"
            cursor.execute(sql_insert, (s_id,))
            conn.commit()
            
            # 3. 오늘 총 횟수 다시 세기
            sql_count = "SELECT COUNT(*) as cnt FROM tb_sensing WHERE sensor_id = %s AND DATE(created_at) = CURDATE()"
            cursor.execute(sql_count, (s_id,))
            result = cursor.fetchone()
            current_count = result['cnt'] if isinstance(result, dict) else result[0]
            
        return jsonify({"count": current_count})
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 시뮬레이션 에러: {e}")
        return jsonify({"count": 0})
    finally:
        conn.close()
        
        
# ==========================================
# 👇 bomi.py 맨 아래에 추가 (주간 활동량 조회 API)
# ==========================================

from datetime import timedelta # 👈 파일 맨 위가 아니라 여기에 써도 작동합니다

@app.route('/api/activity-weekly', methods=['POST'])
def activity_weekly():
    data = request.get_json()
    user_id = data.get('username')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. 모션 센서 ID 찾기
        sql_sensor = """
            SELECT s.sensor_id 
            FROM tb_sensor s
            JOIN tb_device d ON s.device_id = d.device_id
            JOIN tb_senior sn ON d.senior_id = sn.senior_id
            JOIN tb_guardian g ON sn.guardian_id = g.guardian_id
            WHERE g.user_id = %s AND s.sensor_type = 'motion'
            LIMIT 1
        """
        cursor.execute(sql_sensor, (user_id,))
        sensor = cursor.fetchone()
        
        # 기본값: 7일치 0으로 채움
        weekly_counts = [0] * 7
        
        if sensor:
            s_id = sensor['sensor_id'] if isinstance(sensor, dict) else sensor[0]
            
            # 2. 오늘 포함 최근 7일치 데이터 조회 (루프 돌며 확실하게 계산)
            today = datetime.now().date()
            
            for i in range(7):
                # 6일 전부터 ~ 오늘까지 날짜 계산
                target_date = today - timedelta(days=(6 - i))
                
                sql_count = """
                    SELECT COUNT(*) as cnt 
                    FROM tb_sensing 
                    WHERE sensor_id = %s AND DATE(created_at) = %s
                """
                cursor.execute(sql_count, (s_id, target_date))
                result = cursor.fetchone()
                count = result['cnt'] if isinstance(result, dict) else result[0]
                
                weekly_counts[i] = count

        return jsonify({"data": weekly_counts})
        
    except Exception as e:
        print(f"❌ 주간 활동량 에러: {e}")
        return jsonify({"data": [0]*7})
    finally:
        conn.close()


# ==========================================
# 👇 bomi.py 맨 아래에 추가 (월간 활동량 조회 API)
# ==========================================

@app.route('/api/activity-monthly', methods=['POST'])
def activity_monthly():
    data = request.get_json()
    user_id = data.get('username')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. 모션 센서 ID 찾기
        sql_sensor = """
            SELECT s.sensor_id 
            FROM tb_sensor s
            JOIN tb_device d ON s.device_id = d.device_id
            JOIN tb_senior sn ON d.senior_id = sn.senior_id
            JOIN tb_guardian g ON sn.guardian_id = g.guardian_id
            WHERE g.user_id = %s AND s.sensor_type = 'motion'
            LIMIT 1
        """
        cursor.execute(sql_sensor, (user_id,))
        sensor = cursor.fetchone()
        
        # 최근 4주 데이터 (기본값 0)
        monthly_counts = [0] * 4
        
        if sensor:
            s_id = sensor['sensor_id'] if isinstance(sensor, dict) else sensor[0]
            today = datetime.now().date()
            
            # 2. 최근 4주간 데이터 조회
            # (i=0: 이번주, i=1: 지난주 ... i=3: 3주전)
            # 그래프는 왼쪽(오래된 것) -> 오른쪽(최신) 순서이므로 역순으로 저장해야 함
            for i in range(4):
                # 주차별 시작일과 종료일 계산 (7일 단위)
                end_date = today - timedelta(days=(i * 7))
                start_date = end_date - timedelta(days=6)
                
                sql_count = """
                    SELECT COUNT(*) as cnt 
                    FROM tb_sensing 
                    WHERE sensor_id = %s 
                    AND DATE(created_at) BETWEEN %s AND %s
                """
                cursor.execute(sql_count, (s_id, start_date, end_date))
                result = cursor.fetchone()
                count = result['cnt'] if isinstance(result, dict) else result[0]
                
                # 리스트의 뒤에서부터 채워넣기 (그래프 순서 맞추기 위함)
                monthly_counts[3 - i] = count

        return jsonify({"data": monthly_counts})
        
    except Exception as e:
        print(f"❌ 월간 활동량 에러: {e}")
        return jsonify({"data": [0]*4})
    finally:
        conn.close()


# ==========================================
# 👇 bomi.py 맨 아래에 추가 (정보 수정 API)
# ==========================================

# 1. 보호자 정보 수정
@app.route('/api/update-guardian', methods=['POST'])
def update_guardian():
    data = request.get_json()
    user_id = data.get('username')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        sql = """
            UPDATE tb_guardian 
            SET phone = %s, post_num = %s, addr1 = %s, addr2 = %s
            WHERE user_id = %s
        """
        cursor.execute(sql, (
            data['phone'], 
            data['zipcode'], 
            data['address'], 
            data['addressDetail'], 
            user_id
        ))
        conn.commit()
        return jsonify({"message": "보호자 정보 수정 성공"})
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 보호자 수정 에러: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# 2. 어르신 정보 수정
@app.route('/api/update-senior', methods=['POST'])
def update_senior():
    data = request.get_json()
    user_id = data.get('username') # 보호자 아이디를 받음
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. 보호자 아이디로 guardian_id(숫자) 찾기
        cursor.execute("SELECT guardian_id FROM tb_guardian WHERE user_id = %s", (user_id,))
        guardian = cursor.fetchone()
        
        if not guardian:
            return jsonify({"error": "보호자 정보를 찾을 수 없습니다."}), 404
            
        g_id = guardian['guardian_id'] if isinstance(guardian, dict) else guardian[0]

        # 2. 해당 보호자가 모시는 어르신 정보 업데이트
        sql = """
            UPDATE tb_senior 
            SET phone = %s, post_num = %s, addr1 = %s, addr2 = %s
            WHERE guardian_id = %s
        """
        cursor.execute(sql, (
            data['phone'], 
            data['zipcode'], 
            data['address'], 
            data['addressDetail'], 
            g_id
        ))
        conn.commit()
        return jsonify({"message": "어르신 정보 수정 성공"})
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 어르신 수정 에러: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# ==========================================
# 👇 bomi.py 맨 아래에 추가 (비밀번호 변경 API)
# ==========================================

@app.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    user_id = data.get('username')
    current_pw = data.get('currentPassword')
    new_pw = data.get('newPassword')

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. 사용자 조회 및 현재 비밀번호 해시 검증
        sql_check = "SELECT * FROM tb_guardian WHERE user_id = %s"
        cursor.execute(sql_check, (user_id,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user.get('password', user[2] if isinstance(user, tuple) else ''), current_pw):
            return jsonify({"error": "현재 비밀번호가 일치하지 않습니다."}), 400

        # 2. 새 비밀번호 해시 암호화
        hashed_new_pw = generate_password_hash(new_pw)

        # 3. 새 비밀번호로 업데이트!
        sql_update = "UPDATE tb_guardian SET password = %s WHERE user_id = %s"
        cursor.execute(sql_update, (hashed_new_pw, user_id))
        conn.commit()
        
        print(f"🔐 비밀번호 변경 완료: {user_id}")
        return jsonify({"message": "비밀번호 변경 성공"})
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 비밀번호 변경 에러: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ==========================================
# 👇 여기부터 복사해서 bomi.py 맨 아래에 붙여넣기
# ==========================================

# [최종 수정] 기기 추가 API (내 어르신 찾아서 등록)
@app.route('/api/add-device', methods=['POST'])
def add_device():
    data = request.get_json()
    
    # 프론트엔드에서 보낸 데이터 받기
    serial = data.get('serial')
    name = data.get('name')
    location = data.get('location')
    user_id = data.get('username') # 👈 로그인한 아이디 받기
    
    conn = get_db()
    if not conn:
        return jsonify({"error": "DB 연결 실패"}), 500
        
    try:
        cursor = conn.cursor()
        
        # 1. 아이디(user_id)로 보호자 정보(guardian_id) 찾기
        sql_find_guardian = "SELECT guardian_id FROM tb_guardian WHERE user_id = %s"
        cursor.execute(sql_find_guardian, (user_id,))
        guardian_result = cursor.fetchone()
        
        if not guardian_result:
            return jsonify({"error": "사용자 정보를 찾을 수 없습니다."}), 404
            
        g_id = guardian_result['guardian_id']
        
        # 2. 보호자 ID로 연결된 어르신(senior_id) 찾기
        sql_find_senior = "SELECT senior_id FROM tb_senior WHERE guardian_id = %s"
        cursor.execute(sql_find_senior, (g_id,))
        senior_result = cursor.fetchone()
        
        if not senior_result:
            return jsonify({"error": "등록된 어르신이 없습니다."}), 404
            
        s_id = senior_result['senior_id'] # 👈 진짜 어르신 ID 찾음!
        
        # 3. 진짜 어르신 ID(s_id)로 기기 등록!
        sql_device = """
            INSERT INTO tb_device (device_uid, device_name, location, senior_id, installed_at)
            VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(sql_device, (serial, name, location, s_id))
        
        new_device_id = cursor.lastrowid
        
        # 4. 센서 테이블 자동 등록 (환경/모션 구분)
        sensor_type = 'env' if '환경' in name else 'motion'
        sql_sensor = """
            INSERT INTO tb_sensor (device_id, sensor_type, created_at)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(sql_sensor, (new_device_id, sensor_type))
        
        conn.commit()
        print(f"✅ 기기 등록 완료: {name} (ID: {new_device_id}) -> 어르신 {s_id}번")
        
        return jsonify({"message": "등록 성공", "device_id": new_device_id})
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 기기 등록 에러: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        
        

# [최종 수정] 실시간 알림 확인 (읽음 처리 로직 삭제!)
@app.route('/api/check-alert')
def check_alert():
    conn = get_db()
    if not conn:
        return jsonify({"error": "DB 연결 실패"}), 500
        
    try:
        cursor = conn.cursor()
        
        # 1. 가장 최근의 '안 읽은(0)' 알림 1개만 조회
        # (읽음 처리를 안 하므로, 계속 같은 알림을 가져올 수 있지만 프론트엔드에서 ID 비교로 걸러냄)
        sql = """
            SELECT alert_id, alert_type, alert_content, sented_at 
            FROM tb_alert 
            WHERE received_yes = 0 
            ORDER BY sented_at DESC 
            LIMIT 1
        """
        cursor.execute(sql)
        alert = cursor.fetchone()
        
        if alert:
            # 2. 날짜 포맷팅
            if isinstance(alert['sented_at'], datetime):
                alert['sented_at'] = alert['sented_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            # ❌ [삭제됨] 여기서 UPDATE를 하면 팝업 뜨자마자 읽음 처리되어 버림!
            # update_sql = "UPDATE tb_alert SET received_yes = 1 WHERE alert_id = %s"
            # cursor.execute(update_sql, (alert['alert_id'],))
            # conn.commit() 
            
            return jsonify(alert)
        
        return jsonify(None)
        
    except Exception as e:
        # SELECT만 하므로 롤백할 필요는 없지만 에러 로깅
        print(f"그라파나 연동 에러: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# ==========================================
# 👇 bomi.py 맨 아래에 추가 (최근 알림 목록 조회)
# ==========================================

@app.route('/api/alert-list', methods=['POST'])
def get_alert_list():
    # 필요하다면 user_id를 받아서 특정 사용자의 알림만 줄 수도 있음
    # data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 최근 알림 5~10개 조회 (이미 읽은 것도 포함)
        sql = """
            SELECT alert_id, alert_type, alert_content, sented_at, received_yes 
            FROM tb_alert 
            ORDER BY sented_at DESC 
            LIMIT 10
        """
        cursor.execute(sql)
        alerts = cursor.fetchall()
        
        # 날짜 포맷팅
        for a in alerts:
            if isinstance(a['sented_at'], datetime):
                a['sented_at'] = a['sented_at'].strftime('%Y-%m-%d %H:%M:%S')
                
        return jsonify(alerts)
        
    except Exception as e:
        print(f"❌ 알림 목록 조회 에러: {e}")
        return jsonify([])
    finally:
        conn.close()


# ==========================================
# 👇 bomi.py 맨 아래에 추가 (모든 알림 읽음 처리)
# ==========================================

@app.route('/api/alert-read-all', methods=['POST'])
def mark_all_read():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # [수정] 조건을 빼고, 현재 테이블에 있는 모든 알림을 확실하게 '읽음' 처리
        sql = "UPDATE tb_alert SET received_yes = 1"  
        # (만약 특정 사용자만 하고 싶다면 WHERE절이 필요하지만, 지금은 전체 처리가 확실함)
        
        cursor.execute(sql)
        conn.commit()
        
        return jsonify({"message": "모든 알림 읽음 처리 완료"})
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 전체 읽음 처리 에러: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()



# ==========================================
# 👇 bomi.py 맨 아래에 추가 (아이디 중복 확인)
# ==========================================

@app.route('/api/check-duplicate', methods=['POST'])
def check_duplicate():
    data = request.get_json()
    user_id = data.get('username')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # DB에 해당 아이디가 몇 개 있는지 세어봄 (0개면 사용 가능)
        sql = "SELECT count(*) as count FROM tb_guardian WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        
        if result['count'] > 0:
            return jsonify({"isDuplicate": True}) # 중복됨
        else:
            return jsonify({"isDuplicate": False}) # 사용 가능
            
    except Exception as e:
        print(f"중복 확인 에러: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ========================================
# 서버 시작 시 모델 로드 (Flask용)
# ========================================
def initialize_voice_models():
    """
    서버 시작 시 음성 분석 모델 로드
    bomi.py의 if __name__ == '__main__': 부분에서 호출
    """
    global speech_analyzer, llm_handler, voice_db_handler, tts_handler
    
    print("\n" + "="*60)
    print("🎤 음성 분석 모델 로딩 중...")
    print("="*60)
    
    # 1. 음성 분석기
    try:
        print("\n[1/3] SpeechAnalyzer 로드 중... (2-3분 소요)")
        speech_analyzer = SpeechAnalyzer()
        print("✅ SpeechAnalyzer 로드 완료!")
    except Exception as e:
        print(f"⚠️ SpeechAnalyzer 로드 실패: {e}")
        speech_analyzer = None
    
    # 2. LLM 핸들러
    try:
        print("\n[2/3] LLMHandler 로드 중...")
        llm_handler = LLMHandler()
        print("✅ LLMHandler 로드 완료!")
    except Exception as e:
        print(f"⚠️ LLMHandler 로드 실패: {e}")
        llm_handler = None
    
    # 3. DB 핸들러
    try:
        print("\n[3/3] VoiceDBHandler 초기화 중...")
        voice_db_handler = VoiceDBHandler()
        if voice_db_handler.connect():
            print("✅ VoiceDBHandler 초기화 완료!")
        else:
            print("⚠️ DB 연결 실패")
            voice_db_handler = None
    except Exception as e:
        print(f"⚠️ VoiceDBHandler 초기화 실패: {e}")
        voice_db_handler = None
    
    print("\n" + "="*60)
    print("✅ 음성 분석 모델 준비 완료!")
    print("="*60 + "\n")
    
    try:
        print("\n[4/4] TTS 핸들러 초기화 중...")
        from tts_handler import EdgeTTSHandler
        
        # 💡💡💡 여기서 목소리를 변경하세요! 💡💡💡
        tts_handler = EdgeTTSHandler(
            voice='sun-hi',  
            # voice='sun-hi',  # 밝고 친절한 목소리
            # voice='seo-hyeon',  # 부드러운 목소리
            # voice='ji-min',  # 차분한 목소리
            rate='+0%'        # 속도 조절: -10% = 느리게, +10% = 빠르게
        )
        print("✅ TTS 핸들러 초기화 완료!")
        print(f"   목소리: {tts_handler.voice_name}")
        print(f"   속도: {tts_handler.rate}")
    except Exception as e:
        print(f"⚠️ TTS 핸들러 초기화 실패: {e}")
        print("   TTS 없이 계속 진행합니다.")
        tts_handler = None
    
    print("\n" + "="*60)
    print("✅ 음성 분석 모델 준비 완료!")
    print("="*60 + "\n")

# ========================================
# 음성 분석 API 엔드포인트
# ========================================
from flask import Response
import json
@app.route('/api/analyze', methods=['POST'])
def analyze_voice():
    """
    음성 파일 분석 엔드포인트 (실시간 진행 상황 전송)
    
    Form Data:
        - audio_file: 음성 파일 (필수)
        - senior_id: 시니어 ID (기본값: 1)
        - sensing_id: 센싱 ID (선택)
        - generate_response: AI 응답 생성 여부 (기본값: true)
    
    Returns:
        SSE Stream: 실시간 진행 상황 + 최종 결과
    """
    
    # ============================================================
    # Phase 1: Request 데이터 먼저 추출 (제너레이터 밖에서!)
    # ============================================================
    
    # 1. 모델 체크
    if not speech_analyzer:
        return jsonify({'error': '음성 분석기가 초기화되지 않았습니다'}), 503
    
    # 2. 파일 체크
    if 'audio_file' not in request.files:
        return jsonify({'error': '음성 파일이 없습니다'}), 400
    
    audio_file = request.files['audio_file']
    if audio_file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
    
    # 3. 파라미터 추출
    senior_id = int(request.form.get('senior_id', 1))
    sensing_id = request.form.get('sensing_id', None)
    generate_response_flag = request.form.get('generate_response', 'true').lower() == 'true'
    
    if not sensing_id:
        print("❌ sensing_id 누락!")
        return jsonify({
            'error': 'sensing_id가 필요합니다. /api/create-voice-session을 먼저 호출하세요.'
        }), 400

    save_sensing_id = int(sensing_id)
    
    print(f"\n{'='*60}")
    print(f"🎤 음성 분석 요청")
    print(f"{'='*60}")
    print(f"파일명: {audio_file.filename}")
    print(f"시니어 ID: {senior_id}")
    print(f"센싱 ID: {sensing_id}")
    print(f"AI 응답 생성: {generate_response_flag}")
    
    # 4. 임시 파일 저장
    try:
        filename = secure_filename(audio_file.filename)
        suffix = os.path.splitext(filename)[1]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            audio_file.save(tmp_file)
            tmp_path = tmp_file.name
        
        print(f"✅ 임시 파일 저장: {tmp_path}")
    
    except Exception as e:
        return jsonify({'error': f'파일 저장 실패: {str(e)}'}), 500
    
    # ============================================================
    # Phase 2: 제너레이터 함수 (실시간 전송)
    # ============================================================
    def generate():
        
        tts_filename = None
        
        try:
            # === Step 1: 파일 저장 완료 ===
            yield f"data: {json.dumps({'step': 1, 'message': '파일 저장 완료'}, ensure_ascii=False)}\n\n"
            
            # === Step 2: 음성 분석 시작 ===
            yield f"data: {json.dumps({'step': 2, 'message': 'STT 음성 인식 중...'}, ensure_ascii=False)}\n\n"
            
            print("\n[분석 시작...]")
            analysis_result = speech_analyzer.analyze(tmp_path)
            
            whisper = analysis_result['features']['whisper']
            emotion = analysis_result['features']['emotion']
            scores = analysis_result['scores']
            
            # 기본값 설정 (에러 방지용 변수)
            final_emotion_label = emotion.get('final_emotion', '중립')
            confidence_value = emotion.get('audio_conf', 0.0)
            final_emotion_score = scores.get('emotion', 70.0)

            print(f"✅ 분석 완료!")
            print(f"   텍스트: {whisper['text']}")
            print(f"   감정: {final_emotion_label} ({confidence_value:.3f})")
            print(f"   점수: {scores['average']:.1f}점")
            
            # === Step 3: STT 완료 알림 ===
            yield f"data: {json.dumps({'step': 3, 'message': 'STT 완료', 'text_preview': whisper['text'][:50]}, ensure_ascii=False)}\n\n"
            
            # === Step 4: AI 응답 생성 및 Q&A 매칭 ===
            ai_response = None
            if generate_response_flag and llm_handler:
                yield f"data: {json.dumps({'step': 5, 'message': 'AI 응답 생성 중...'}, ensure_ascii=False)}\n\n"
                
                try:
                    print("\n[AI 응답 생성 중...]")
                    ai_response = llm_handler.chat(
                        whisper['text'],
                        emotion_info=emotion,
                        scores=scores
                    )
                    
                    # Q&A 매칭 정보 확인 (점수 덮어쓰기 로직)
                    qa_match_info = llm_handler.get_last_qa_match()
                    if qa_match_info and qa_match_info.get('matched'):
                        print(f"✅ Q&A 매칭 성공! 데이터셋 점수를 적용합니다.")
                        final_emotion_label = qa_match_info.get('emotion')
                        final_emotion_score = qa_match_info.get('emotion_score')
                        confidence_value = final_emotion_score / 100.0
                        
                        # 원본 객체 업데이트 (DB 저장 및 최종 결과용)
                        emotion['final_emotion'] = final_emotion_label
                        emotion['audio_conf'] = confidence_value
                        scores['emotion'] = final_emotion_score
                    
                    print(f"✅ AI 응답: {ai_response[:50]}...")
                    if tts_handler and ai_response:
                        yield f"data: {json.dumps({'step': 5.5, 'message': '목소리 만드는 중...'}, ensure_ascii=False)}\n\n"
                        
                        try:
                            # 1. [강제 설정] 경로 변수, 밖에서 가져오지 말고 여기서 직접 만듭니다. (에러 원천 차단)
                            current_dir = os.path.dirname(os.path.abspath(__file__))
                            output_folder = os.path.join(current_dir, 'tts_outputs')
                            os.makedirs(output_folder, exist_ok=True)
                            
                            # 2. [강제 설정] 파일명도 여기서 바로 만듭니다.
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            tts_filename = f"response_{timestamp}.mp3"
                            
                            # 3. 경로 합치기 (이제 둘 다 확실히 있으니까 None 에러 절대 안 남!)
                            tts_file_path = os.path.join(output_folder, tts_filename)
                            print(f"🎤 저장할 경로: {tts_file_path}") 

                            # 4. 저장 실행
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            # (혹시 모를 문자열 변환 추가)
                            communicate = tts_handler.edge_tts.Communicate(
                                text=str(ai_response), 
                                voice=tts_handler.voice,
                                rate=tts_handler.rate
                            )
                            loop.run_until_complete(communicate.save(tts_file_path))
                            loop.close()

                            print(f"✅ TTS 생성 성공!")
                            yield f"data: {json.dumps({'step': 5.7, 'message': 'TTS 완료', 'tts_file': tts_filename, 'ai_response': ai_response}, ensure_ascii=False)}\n\n"
                        
                        except Exception as e:
                            print(f"⚠️ TTS 만들다 실패: {e}")
                            # 실패해도 AI 응답은 보내줍니다
                            yield f"data: {json.dumps({'step': 5.7, 'message': 'TTS 실패', 'error': str(e), 'ai_response': ai_response}, ensure_ascii=False)}\n\n"
                    
                            
                        except Exception as tts_error:
                            print(f"⚠️ TTS 생성 실패: {tts_error}")
                            import traceback
                            traceback.print_exc()
                            # TTS 실패해도 ai_response는 전송
                            yield f"data: {json.dumps({'step': 5.7, 'message': 'TTS 실패', 'error': str(tts_error), 'ai_response': ai_response}, ensure_ascii=False)}\n\n"
                    else:
                        # TTS 핸들러 없거나 비활성화 (ai_response는 전송)
                        if not tts_handler:
                            print("⚠️ TTS 핸들러가 초기화되지 않았습니다")
                        yield f"data: {json.dumps({'step': 5.7, 'message': 'TTS 비활성화', 'ai_response': ai_response}, ensure_ascii=False)}\n\n"
                except Exception as e:
                    print(f"⚠️ AI 응답 생성 실패: {e}")
                    ai_response = "죄송해요, 지금은 답변을 만들 수 없어요. 다시 말씀해주시겠어요?"

            # === Step 5: 감정 분석 결과 알림 (수정됨) ===
            # Q&A 결과가 반영된 confidence_value를 사용하여 53%가 나오게 함
            emotion_msg = f"{final_emotion_label} ({confidence_value*100:.0f}%)"
            yield f"data: {json.dumps({'step': 4, 'message': f'감정 분석: {emotion_msg}'}, ensure_ascii=False)}\n\n"
            
            # === Step 6: DB 저장 ===
            yield f"data: {json.dumps({'step': 6, 'message': 'DB 저장 중...'}, ensure_ascii=False)}\n\n"
            
            voice_id = None
            if voice_db_handler:
                try:
                    print(f"\n[DB 저장 중... (sensing_id={save_sensing_id})]")
                    voice_id = voice_db_handler.save_analysis(
                        senior_id,
                        analysis_result,
                        save_sensing_id
                    )
                    if voice_id:
                        print(f"✅ DB 저장 완료 (voice_id: {voice_id})")
                except Exception as e:
                    print(f"❌ DB 저장 에러: {e}")
            
            # === Step 7: 임시 파일 삭제 ===
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    print(f"🗑️ 임시 파일 삭제: {tmp_path}")
            except Exception as e:
                print(f"⚠️ 파일 삭제 실패: {e}")
            
            # === Step 8: 최종 결과 반환 (KeyError 방지 수정) ===
            result = {
                'step': 'complete',
                'success': True,
                'voice_id': voice_id,
                'analysis': {
                    'text': whisper['text'],
                    'emotion': {
                        'final': final_emotion_label,
                        'confidence': confidence_value,
                        'text_emotion': emotion.get('text_label', '중립'), # text_emotion -> text_label
                        'audio_emotion': emotion.get('audio_label', '중립'), # audio_emotion -> audio_label
                        'z_peak': emotion.get('z_peak', 0.0),
                        'decision': "분석 완료" # decision 키가 없으므로 고정문구 사용
                    },
                    'scores': scores,
                    'whisper': whisper
                },
                'ai_response': ai_response,
                'tts_file': tts_filename,
                'metadata': {
                    'senior_id': senior_id,
                    'sensing_id': save_sensing_id if voice_db_handler else None,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
            print(f"\n{'='*60}\n✅ 응답 전송 완료\n{'='*60}\n")
        
        except Exception as e:
            # (에러 처리 로직 동일...)
            print(f"\n❌ 오류 발생! 타입: {type(e).__name__}, 메시지: {str(e)}")
            import traceback
            traceback.print_exc()
            error_result = {'step': 'error', 'error': str(e)}
            yield f"data: {json.dumps(error_result, ensure_ascii=False)}\n\n"
    
    # ============================================================
    # Phase 3: SSE 응답 반환
    # ============================================================
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

@app.route('/api/tts-audio/<path:filename>')
def serve_tts_audio(filename):
    # bomi.py에서 tts_dir = './tts_outputs' 로 설정했으므로 거기서 꺼내줌
    return send_from_directory(TTS_FOLDER, filename)

# ========================================
# 서버 상태 확인 엔드포인트 (선택)
# ========================================
@app.route('/api/voice-health', methods=['GET'])
def voice_health():
    """음성 분석 시스템 상태 확인"""
    return jsonify({
        'analyzer': speech_analyzer is not None,
        'llm': llm_handler is not None,
        'db': voice_db_handler is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/check-sensor', methods=['GET', 'POST'])
def check_sensor():
    """
    시니어의 센서 존재 여부 확인
    - 녹음 버튼 활성화/비활성화에 사용
    
    POST Body (JSON):
        username: 보호자 아이디
    
    또는 GET 파라미터:
        username: 보호자 아이디
    
    Returns:
        has_sensor: 센서 존재 여부
        sensor_id: 센서 ID
        sensor_type: 센서 타입
        device_name: 디바이스 이름
    """
    
    # POST 또는 GET으로 username 받기
    if request.method == 'POST':
        data = request.get_json()
        user_id = data.get('username')
    else:
        user_id = request.args.get('username')
    
    if not user_id:
        return jsonify({
            "has_sensor": False,
            "message": "사용자 아이디가 필요합니다"
        }), 400
    
    conn = get_db()
    if not conn:
        return jsonify({
            "has_sensor": False,
            "message": "DB 연결 실패"
        }), 500
    
    try:
        cursor = conn.cursor()
        
        # 보호자 → 어르신 → 디바이스 → 센서 찾기
        sql = """
            SELECT 
                s.sensor_id, 
                s.sensor_type,
                d.device_id,
                d.device_name,
                d.location
            FROM tb_sensor s
            JOIN tb_device d ON s.device_id = d.device_id
            JOIN tb_senior sn ON d.senior_id = sn.senior_id
            JOIN tb_guardian g ON sn.guardian_id = g.guardian_id
            WHERE g.user_id = %s
            ORDER BY s.created_at DESC
            LIMIT 1
        """
        
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        
        if result:
            return jsonify({
                "has_sensor": True,
                "sensor_id": result['sensor_id'],
                "sensor_type": result['sensor_type'],
                "device_id": result['device_id'],
                "device_name": result['device_name'],
                "location": result['location'],
                "message": f"센서 사용 가능 ({result['device_name']})"
            })
        else:
            return jsonify({
                "has_sensor": False,
                "message": "등록된 센서가 없습니다. 센서를 먼저 등록해주세요."
            })
    
    except Exception as e:
        print(f"❌ 센서 확인 실패: {e}")
        return jsonify({
            "has_sensor": False,
            "error": str(e)
        }), 500
    
    finally:
        conn.close()


@app.route('/api/create-voice-session', methods=['POST'])
def create_voice_session():
    """
    음성 녹음 세션 시작
    1. 보호자의 센서 찾기
    2. tb_sensing에 음성 세션 레코드 생성
    3. sensing_id 반환
    
    POST Body (JSON):
        username: 보호자 아이디
    
    Returns:
        success: 성공 여부
        sensing_id: 생성된 센싱 ID
        sensor_id: 사용된 센서 ID
    """
    
    data = request.get_json()
    user_id = data.get('username')
    
    if not user_id:
        return jsonify({
            "success": False,
            "message": "사용자 아이디가 필요합니다"
        }), 400
    
    conn = get_db()
    if not conn:
        return jsonify({
            "success": False,
            "message": "DB 연결 실패"
        }), 500
    
    try:
        cursor = conn.cursor()
        
        print(f"\n{'='*60}")
        print(f"🎙️ 음성 세션 생성 요청")
        print(f"{'='*60}")
        print(f"보호자 ID: {user_id}")
        
        # 1. 보호자의 센서 찾기
        find_sensor_sql = """
            SELECT s.sensor_id, s.sensor_type, d.device_name
            FROM tb_sensor s
            JOIN tb_device d ON s.device_id = d.device_id
            JOIN tb_senior sn ON d.senior_id = sn.senior_id
            JOIN tb_guardian g ON sn.guardian_id = g.guardian_id
            WHERE g.user_id = %s
            ORDER BY s.created_at DESC
            LIMIT 1
        """
        
        cursor.execute(find_sensor_sql, (user_id,))
        sensor_result = cursor.fetchone()
        
        if not sensor_result:
            print(f"❌ 보호자 {user_id}의 센서를 찾을 수 없음")
            return jsonify({
                "success": False,
                "message": "센서를 찾을 수 없습니다. 센서를 먼저 등록해주세요."
            }), 404
        
        sensor_id = sensor_result['sensor_id']
        sensor_type = sensor_result['sensor_type']
        device_name = sensor_result['device_name']
        
        print(f"✅ 센서 발견:")
        print(f"   sensor_id: {sensor_id}")
        print(f"   sensor_type: {sensor_type}")
        print(f"   device: {device_name}")
        
        # 2. tb_sensing에 음성 세션 레코드 생성
        create_sensing_sql = """
            INSERT INTO tb_sensing 
            (sensor_id, sensing_type, sensing_value) 
            VALUES (%s, 'voice_session', 'recording_start')
        """
        
        cursor.execute(create_sensing_sql, (sensor_id,))
        conn.commit()
        
        # 3. 방금 생성한 sensing_id 가져오기
        sensing_id = cursor.lastrowid
        
        print(f"✅ 음성 세션 생성 완료!")
        print(f"   sensing_id: {sensing_id}")
        print(f"{'='*60}\n")
        
        return jsonify({
            "success": True,
            "sensing_id": sensing_id,
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "device_name": device_name,
            "message": "음성 세션이 시작되었습니다"
        })
    
    except Exception as e:
        conn.rollback()
        print(f"❌ 음성 세션 생성 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
    finally:
        conn.close()



# 인증서 추가 할려면?(pyopenssl 라이브러리 필요): 
# python generate_cert.py
if __name__ == '__main__':
    # 🎤 음성 분석 모델 로드 (서버 시작 전!)
    initialize_voice_models()
    
    # Flask 서버 시작
    app.run(debug=True, host='0.0.0.0', port=5000)