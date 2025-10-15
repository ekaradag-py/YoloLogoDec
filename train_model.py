from ultralytics import YOLO
import os

def train_logo_model():
    """
    YOLOv8 modelini, Roboflow'dan indirilen veri setiyle eğitir.
    """
    model = YOLO('yolov8n.pt')

    data_yaml_path = os.path.join('dataset', 'Logo-Brand-2', 'data.yaml')

    print(f"Veri seti yapılandırma dosyası okunuyor: {data_yaml_path}")
    print("Model eğitimi başlıyor... Bu işlem bilgisayarınızın gücüne bağlı olarak uzun sürebilir.")

    results = model.train(
        data=data_yaml_path,
        epochs=50,  
        imgsz=640
    )

    print("Eğitim tamamlandı!")
    print("Eğitilmiş modelin sonuçları 'runs/detect/' klasörüne kaydedildi.")

if __name__ == '__main__':
    train_logo_model()