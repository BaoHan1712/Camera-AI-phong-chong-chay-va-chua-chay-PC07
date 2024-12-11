import os
import cv2
import numpy as np
import random
from pathlib import Path

def is_grayscale(image_path):
    """Kiểm tra xem ảnh có phải là ảnh xám không"""
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            return False
        
        # Chuyển sang HSV và tính độ bão hòa trung bình
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mean_saturation = np.mean(hsv[:, :, 1])
        
        # Kiểm tra thêm độ tương phản
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contrast = np.std(gray)
        
        # Điều kiện để xác định ảnh xám:
        # 1. Độ bão hòa thấp (< 15)
        # 2. Độ tương phản không quá cao (< 50)
        return mean_saturation < 25 and contrast < 80
    except Exception as e:
        print(f"Lỗi khi xử lý ảnh {image_path}: {e}")
        return False

def show_sample_images(gray_images):
    """Hiển thị các ảnh mẫu và chờ phản hồi từ người dùng"""
    sample_size = min(3, len(gray_images))
    random_samples = random.sample(gray_images, sample_size)
    
    # Tạo cửa sổ hiển thị ảnh với kích thước cố định
    window_width = 400
    for i, img_path in enumerate(random_samples):
        img = cv2.imread(str(img_path))
        if img is not None:
            # Thay đổi kích thước ảnh để hiển thị
            height = int(img.shape[0] * window_width / img.shape[1])
            img_resized = cv2.resize(img, (window_width, height))
            
            # Hiển thị tên file trên ảnh
            window_name = f'Ảnh xám mẫu {i+1} - {img_path.name}'
            cv2.imshow(window_name, img_resized)
            # Di chuyển cửa sổ để không bị chồng lên nhau
            cv2.moveWindow(window_name, window_width * i, 0)

def main():
    # Đường dẫn thư mục mặc định
    folder_path = Path("y\d\images")
    
    if not folder_path.exists():
        print(f"Thư mục {folder_path} không tồn tại!")
        return
    
    # Lấy danh sách các file ảnh
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    image_files = [f for f in folder_path.glob('*') if f.suffix.lower() in image_extensions]
    
    if not image_files:
        print("Không tìm thấy file ảnh nào trong thư mục!")
        return
    
    # Tìm các ảnh xám
    print("Đang quét tìm ảnh xám...")
    gray_images = [img_path for img_path in image_files if is_grayscale(img_path)]
    
    if not gray_images:
        print("Không tìm thấy ảnh xám trong thư mục!")
        return
    
    print(f"\nTìm thấy {len(gray_images)} ảnh xám trong tổng số {len(image_files)} ảnh")
    
    # Hiển thị ảnh mẫu
    show_sample_images(gray_images)
    
    print("\nĐang hiển thị các ảnh xám mẫu...")
    print("Nhấn 'c' để xác nhận xóa TẤT CẢ ảnh xám")
    print("Nhấn phím bất kỳ khác để HỦY")
    
    # Đợi phản hồi từ người dùng
    key = cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if key == ord('c'):
        # Xóa tất cả ảnh xám
        deleted_count = 0
        for img_path in gray_images:
            try:
                os.remove(img_path)
                print(f"Đã xóa: {img_path.name}")
                deleted_count += 1
            except Exception as e:
                print(f"Lỗi khi xóa {img_path.name}: {e}")
        
        print(f"\nĐã xóa thành công {deleted_count}/{len(gray_images)} ảnh xám")
    else:
        print("Đã hủy thao tác xóa")

if __name__ == "__main__":
    main()