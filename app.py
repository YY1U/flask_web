from flask import Flask, render_template, request, jsonify
import random
import requests # สำหรับการเรียก API ของ RPC server

app = Flask(__name__)

# ฟังก์ชันสำหรับสร้างโจทย์คณิตศาสตร์ง่ายๆ
def generate_math_problem():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operator = random.choice(['+', '-', '*', '/']) # ยังไม่รวมหารเพื่อความง่าย
    problem = f"{num1} {operator} {num2}"
    
    # คำนวณคำตอบ
    if operator == '+':
        answer = num1 + num2
    elif operator == '-':
        answer = num1 - num2
    elif operator == '*':
        answer = num1 * num2
    elif operator == '/':
        # ตรวจสอบให้แน่ใจว่าหารลงตัว
        if num1 % num2 != 0:
            return generate_math_problem() # สร้างโจทย์ใหม่ถ้าหารไม่ลงตัว
        answer = num1 // num2
    
    return {'problem': problem, 'answer': answer}

# กำหนดเส้นทางสำหรับหน้าหลัก
@app.route('/')
def index():
    problem_data = generate_math_problem()
    return render_template('index.html', problem=problem_data['problem'])

# API สำหรับขอโจทย์ใหม่
@app.route('/new_problem', methods=['GET'])
def new_problem():
    problem_data = generate_math_problem()
    return jsonify({'problem': problem_data['problem']})

# API สำหรับขอ Hint (ตัวอย่าง)
@app.route('/get_hint', methods=['POST'])
def get_hint():
    # ในความเป็นจริง ควรมีการใช้ LLM หรือ Logic ซับซ้อนกว่านี้
    current_problem = request.json.get('problem')
    hint_text = f"ลองดูดีๆ นะว่าเครื่องหมาย {current_problem.split()[1]} หมายถึงอะไร!"
    if current_problem.split()[1] == '+':
        hint_text = "การบวกคือการรวมกันของจำนวนสองจำนวน"
    elif current_problem.split()[1] == '-':
        hint_text = "การลบคือการหักออกของจำนวนหนึ่งจากอีกจำนวนหนึ่ง"
    elif current_problem.split()[1] == '*':
        hint_text = "การคูณคือการบวกซ้ำๆ ของจำนวนเดียวกัน"
    elif current_problem.split()[1] == '/':
        hint_text = "การหารคือการแบ่งจำนวนออกเป็นส่วนๆ เท่าๆ กัน"
    
    return jsonify({'hint': hint_text})

# API สำหรับ Live Helping (จำลอง) - อาจส่งข้อมูลภาพไปให้ LLM หรือ Human Helper
@app.route('/live_helping', methods=['POST'])
def live_helping():
    # ในโลกจริง ตรงนี้คุณจะส่งข้อมูลภาพกระดาน หรือข้อความไปประมวลผลด้วย LLM
    # หรือส่งไปให้มนุษย์ช่วยดู
    data = request.json
    drawing_data = data.get('drawing') # ข้อมูลภาพจากกระดานเขียน
    user_question = data.get('question') # คำถามที่ผู้ใช้อาจพิมพ์เข้ามา

    # ตัวอย่างการตอบกลับแบบจำลอง
    response_text = "กำลังเชื่อมต่อผู้ช่วย... กรุณารอสักครู่ (ในโลกจริงอาจมีระบบ AI หรือคนมาตอบ)"
    if user_question:
        response_text = f"คุณถามว่า '{user_question}' ใช่ไหม? กำลังหาผู้ช่วยให้ครับ..."
    
    # ถ้ามีการส่งภาพกระดาน คุณอาจจะส่งไปยัง Image Processing/LLM Engine ของ Screen Pilot Realtime
    # แต่ตอนนี้เราจำลองการตอบกลับ
    
    return jsonify({'help': response_text})

'''@app.route('/live_helping', methods=['POST'])
def live_helping():
    data = request.json
    drawing_data = data.get('drawing') # Base64 image
    user_question = data.get('question')
     # ส่วนนี้คือการเชื่อมต่อกับ Screen Pilot Realtime
    try:
        # สมมติว่า image-processing ของ Screen Pilot Realtime คาดหวัง JSON ที่มี 'image_data'
        screen_pilot_response = requests.post(
            "https://api.hackathon2025.ai.in.th/team14-1:2402/img-process", # URL ของ image-processing
            json={'image_data': drawing_data, 'user_question': user_question} # อาจส่งคำถามไปด้วย
        )
        screen_pilot_response.raise_for_status() # ตรวจสอบ error
        processed_data = screen_pilot_response.json()

        # ผลลัพธ์จาก Screen Pilot Realtime อาจจะอยู่ในรูปแบบที่คุณกำหนด
        # เช่น processed_data['description'], processed_data['suggestion']
        response_text = processed_data.get('description', 'ไม่สามารถวิเคราะห์ได้')
        if processed_data.get('suggestion'):
            response_text += f" (คำแนะนำ: {processed_data['suggestion']})"

        # หรือคุณอาจต้องส่งต่อไปยัง LLM-engine และ Post-processing ของ Screen Pilot อีกที
        # ขึ้นอยู่กับว่า img-process ทำอะไรให้บ้าง และ LLM-engine/Post-processing ของคุณเป็น API อย่างไร
        # (จากที่คุณบอก Architecture Flow, Client -> queue-management-system -> image-processing -> llm-engine -> post-processing)
        # ดังนั้น Flask จะเป็น Client ของ queue-management-system แทน
        
        # สำหรับโปรเจกต์คุณ Client -> queue-management-system
        # ดังนั้น Flask จะต้องส่ง request ไปที่ queue-management-system/ws
        # แต่เนื่องจากเป็น WebSocket อาจต้องใช้ไลบรารีที่รองรับ WebSocket client ใน Flask
        # หรือถ้า queue-management-system มี HTTP API สำหรับรับคำขอด้วย ก็จะง่ายกว่า

        # ถ้า queue-management-system มี HTTP API:
        # req_data = {'image_data': drawing_data, 'question': user_question}
        # sp_response = requests.post(
        #     "https://api.hackathon2025.ai.in.th/team14-1:2401/some_http_endpoint_for_image_and_question",
        #     json=req_data
        # )
        # processed_data = sp_response.json()
        # response_text = processed_data.get('response_from_llm')

    except requests.exceptions.RequestException as e:
        print(f"Error calling Screen Pilot Realtime API: {e}")
        response_text = "เกิดข้อผิดพลาดในการเชื่อมต่อระบบช่วยเหลือ"
    
    return jsonify({'help': response_text})'''

if __name__ == '__main__':
    app.run(debug=True)