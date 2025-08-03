document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('drawing-board');
    const ctx = canvas.getContext('2d');
    const clearBtn = document.getElementById('clear-board-btn');
    const colorPicker = document.getElementById('color-picker');
    const brushSize = document.getElementById('brush-size');
    const brushSizeDisplay = document.getElementById('brush-size-display');
    const hintBtn = document.getElementById('hint-btn');
    const liveHelpBtn = document.getElementById('live-help-btn');
    const newProblemBtn = document.getElementById('new-problem-btn');
    const mathProblemDiv = document.getElementById('math-problem');
    const feedbackDiv = document.getElementById('feedback');

    let drawing = false;
    let currentX = 0;
    let currentY = 0;
    let currentColor = colorPicker.value;
    let currentBrushSize = brushSize.value;

    // --- Drawing Board Logic ---
    function getMousePos(event) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
    }

    function getTouchPos(event) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: event.touches[0].clientX - rect.left,
            y: event.touches[0].clientY - rect.top
        };
    }

    function drawLine(x1, y1, x2, y2) {
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = currentColor;
        ctx.lineWidth = currentBrushSize;
        ctx.lineCap = 'round';
        ctx.stroke();
    }

    // Mouse events
    canvas.addEventListener('mousedown', (e) => {
        drawing = true;
        const pos = getMousePos(e);
        currentX = pos.x;
        currentY = pos.y;
    });

    canvas.addEventListener('mousemove', (e) => {
        if (!drawing) return;
        const pos = getMousePos(e);
        drawLine(currentX, currentY, pos.x, pos.y);
        currentX = pos.x;
        currentY = pos.y;
    });

    canvas.addEventListener('mouseup', () => {
        drawing = false;
    });

    canvas.addEventListener('mouseout', () => {
        drawing = false;
    });

    // Touch events (for mobile/tablet)
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault(); // Prevent scrolling
        drawing = true;
        const pos = getTouchPos(e);
        currentX = pos.x;
        currentY = pos.y;
    });

    canvas.addEventListener('touchmove', (e) => {
        e.preventDefault(); // Prevent scrolling
        if (!drawing) return;
        const pos = getTouchPos(e);
        drawLine(currentX, currentY, pos.x, pos.y);
        currentX = pos.x;
        currentY = pos.y;
    });

    canvas.addEventListener('touchend', () => {
        drawing = false;
    });

    clearBtn.addEventListener('click', () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    });

    colorPicker.addEventListener('input', (e) => {
        currentColor = e.target.value;
    });

    brushSize.addEventListener('input', (e) => {
        currentBrushSize = e.target.value;
        brushSizeDisplay.textContent = `${currentBrushSize} px`;
    });

    // --- Button Logic ---
    hintBtn.addEventListener('click', async () => {
        const currentProblem = mathProblemDiv.textContent;
        feedbackDiv.classList.remove('success'); // Clear previous styles
        feedbackDiv.classList.add('active'); // Show feedback area

        try {
            const response = await fetch('/get_hint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ problem: currentProblem })
            });
            const data = await response.json();
            feedbackDiv.textContent = `คำใบ้: ${data.hint}`;
        } catch (error) {
            console.error('Error getting hint:', error);
            feedbackDiv.textContent = 'ไม่สามารถดึงคำใบ้ได้ในขณะนี้';
        }
    });

    liveHelpBtn.addEventListener('click', async () => {
        // ดึงข้อมูลภาพจากกระดานเขียนเป็น Base64
        const imageData = canvas.toDataURL('image/png'); // หรือ image/jpeg

        feedbackDiv.classList.remove('success'); // Clear previous styles
        feedbackDiv.classList.add('active'); // Show feedback area
        feedbackDiv.textContent = 'กำลังเชื่อมต่อกับผู้ช่วย...';

        try {
            const response = await fetch('/live_helping', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    drawing: imageData, // ส่งข้อมูลภาพ
                    question: prompt("คุณมีคำถามอะไรเพิ่มเติมเกี่ยวกับโจทย์นี้ไหมครับ? (พิมพ์แล้วกด OK)") // ถามคำถามเพิ่มเติม
                })
            });
            const data = await response.json();
            feedbackDiv.textContent = `ผู้ช่วย: ${data.help}`;
            // ถ้าเป็นระบบจริง อาจจะเปิด WebSocket เพื่อการสื่อสารแบบ Realtime
        } catch (error) {
            console.error('Error requesting live helping:', error);
            feedbackDiv.textContent = 'ไม่สามารถเชื่อมต่อ Live Helping ได้ในขณะนี้';
        }
    });

    newProblemBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/new_problem');
            const data = await response.json();
            mathProblemDiv.textContent = data.problem;
            ctx.clearRect(0, 0, canvas.width, canvas.height); // ล้างกระดานเมื่อได้โจทย์ใหม่
            feedbackDiv.classList.remove('active', 'success'); // ซ่อน feedback
            feedbackDiv.textContent = '';
        } catch (error) {
            console.error('Error getting new problem:', error);
            mathProblemDiv.textContent = 'เกิดข้อผิดพลาดในการโหลดโจทย์';
        }
    });
});