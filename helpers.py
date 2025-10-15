import os
import cv2
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import uuid
from collections import defaultdict

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

print("YOLOv8 modeli yükleniyor...")
model = YOLO('best.pt')
print("Model başarıyla yüklendi.")


def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- RESİM ANALİZ FONKSİYONU  ---
def analyze_image_with_yolo(file):
    if not (file and is_allowed_file(file.filename)): return None, None
    filename = secure_filename(file.filename)
    original_filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(original_filepath)
    try:
        results = model(original_filepath)
    except Exception as e:
        print(f"Model tahmini sırasında hata: {e}")
        return None, None
    detections = []
    annotated_filename = None
    for result in results:
        annotated_filename = f"result_{uuid.uuid4()}.jpg"
        annotated_filepath = os.path.join(UPLOAD_FOLDER, annotated_filename)
        result.save(filename=annotated_filepath)
        for box in result.boxes:
            class_id = int(box.cls[0])
            brand_name = model.names[class_id]
            confidence = float(box.conf[0])
            detections.append({'brand': brand_name, 'confidence': f"{confidence * 100:.2f}%"})
    return detections, annotated_filename

# --- VİDEO ANALİZ FONKSİYONU ---

def analyze_video_with_yolo(file):
    if not (file and is_allowed_file(file.filename)): return None, None

    filename = secure_filename(file.filename)
    input_video_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_video_path)

    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Hata: Video dosyası açılamadı.")
        return None, None

    logo_counts = defaultdict(int) 
    total_detections = 0
    tracked_ids = set() 

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    output_filename = f"result_{uuid.uuid4()}.mp4"
    output_video_path = os.path.join(UPLOAD_FOLDER, output_filename)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    # 5. Videoyu kare kare işle
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(source=frame, persist=True)

        # Sonuçları işle
        if results and results[0].boxes.id is not None:
            annotated_frame = results[0].plot()
            for box in results[0].boxes:
                track_id = int(box.id[0])

                if track_id not in tracked_ids:
                    tracked_ids.add(track_id)
                    total_detections += 1
                    class_id = int(box.cls[0])
                    brand_name = model.names[class_id]
                    logo_counts[brand_name] += 1
        else:
            annotated_frame = frame
        
        out.write(annotated_frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    final_results = {
        "total_detections": total_detections,
        "logo_counts": dict(logo_counts)
    }

    return final_results, output_filename

    if not (file and is_allowed_file(file.filename)): return None, None

    # 1. Gelen videoyu kaydet
    filename = secure_filename(file.filename)
    input_video_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_video_path)

    # 2. Videoyu okumak için OpenCV'yi kullan
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Hata: Video dosyası açılamadı.")
        return None, None

    # 3. Sonuçları ve sayımları tutacak değişkenleri oluştur
    logo_counts = defaultdict(int) # Hangi logodan kaç tane var?
    total_detections = 0

    # 4. İşlenmiş videoyu yazmak için ayarları yap
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    output_filename = f"result_{uuid.uuid4()}.mp4"
    output_video_path = os.path.join(UPLOAD_FOLDER, output_filename)
    # MP4 formatı için 'mp4v' codec'ini kullanıyoruz
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    # 5. Videoyu kare kare işle
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # YOLOv8 modelini mevcut kare üzerinde çalıştır
        #results = model(frame)
        results = model.track(source=frame, persist=True)
        # Sonuçları işle
        for result in results:
            # Tespit edilen logo sayılarını güncelle
            num_detections_in_frame = len(result.boxes)
            if num_detections_in_frame > 0:
                total_detections += num_detections_in_frame
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    brand_name = model.names[class_id]
                    logo_counts[brand_name] += 1
            
            # Üzerinde kutular çizilmiş kareyi al
            annotated_frame = result.plot()
            # Bu kareyi yeni videoya yaz
            out.write(annotated_frame)

    # 6. Her şeyi serbest bırak
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Sonuçları paketle
    final_results = {
        "total_detections": total_detections,
        "logo_counts": dict(logo_counts) # defaultdict'u normal dict'e çevir
    }

    return final_results, output_filename