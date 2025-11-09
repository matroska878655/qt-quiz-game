FROM cdrx/pyinstaller-windows:python3
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pyinstaller \
    --name "QuizMasterPro" \
    --onefile \
    --windowed \
    --icon=icon.ico \
    --add-data "default_questions.json;." \
    --hidden-import "arabic_reshaper" \
    --hidden-import "bidi.algorithm" \
    quiz_app.py
