from ultralytics import YOLO
import os

def validate_trained_model():
    print("Eğitilmiş model yükleniyor: best.pt")
    model = YOLO('best.pt')
    data_yaml_path = os.path.join('dataset', 'Logo-Brand-2', 'data.yaml')
    print(f"Veri seti '{data_yaml_path}' kullanılarak doğrulama işlemi başlatılıyor...")
    print("Bu işlem, test setindeki tüm görseller işleneceği için birkaç dakika sürebilir.")
    
    metrics = model.val(
        data=data_yaml_path,
        split='test'
    )

    print("\n--- Doğrulama Sonuçları ---")
    print(f"mAP50-95 Skoru: {metrics.box.map:.4f}")   # En genel ve standart mAP skoru
    print(f"mAP50 Skoru: {metrics.box.map50:.4f}")     # Daha az katı olan mAP skoru
    print(f"Precision (Kesinlik): {metrics.box.mp:.4f}")
    print(f"Recall (Duyarlılık): {metrics.box.mr:.4f}")
    print("\nDetaylı sonuçlar ve grafikler 'runs/detect/val/' klasörüne kaydedildi.")

if __name__ == '__main__':
    validate_trained_model()