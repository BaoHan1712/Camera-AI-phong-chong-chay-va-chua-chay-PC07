import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from imagehash import average_hash, phash, dhash
import itertools

def get_image_hashes(image_path):
    """Tính toán nhiều loại hash của ảnh để so sánh chính xác hơn"""
    try:
        img = Image.open(image_path)
        # Kết hợp 3 loại hash để tăng độ chính xác
        return {
            'average': str(average_hash(img, hash_size=16)),
            'phash': str(phash(img, hash_size=16)),
            'dhash': str(dhash(img, hash_size=16))
        }
    except Exception as e:
        print(f"Lỗi khi xử lý ảnh {image_path}: {e}")
        return None

def calculate_similarity(hash1, hash2):
    """Tính độ tương đồng giữa hai hash"""
    if not (hash1 and hash2):
        return 0
    
    # Tính trung bình độ tương đồng của cả 3 loại hash
    similarities = []
    for hash_type in ['average', 'phash', 'dhash']:
        h1 = int(hash1[hash_type], 16)
        h2 = int(hash2[hash_type], 16)
        # Tính số bit khác nhau
        hamming_distance = bin(h1 ^ h2).count('1')
        # Chuyển đổi thành phần trăm giống nhau
        similarity = (650 - hamming_distance) / 650 * 100
        similarities.append(similarity)
    
    return sum(similarities) / len(similarities)

def find_similar_images(folder_path, similarity_threshold=85):
    """Tìm các ảnh gần giống nhau trong thư mục"""
    image_hashes = {}
    similar_groups = []
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    print("Đang quét và tính toán hash của tất cả ảnh...")
    # Thu thập tất cả ảnh và hash
    for img_path in Path(folder_path).glob('*'):
        if img_path.suffix.lower() in image_extensions:
            hashes = get_image_hashes(img_path)
            if hashes:
                image_hashes[img_path] = hashes
    
    print("Đang tìm ảnh tương tự...")
    # So sánh từng cặp ảnh
    processed_images = set()
    for img1, img2 in itertools.combinations(image_hashes.keys(), 2):
        if img1 not in processed_images:
            current_group = []
            similarity = calculate_similarity(image_hashes[img1], image_hashes[img2])
            
            if similarity >= similarity_threshold:
                if not current_group:
                    current_group.append(img1)
                current_group.append(img2)
                processed_images.add(img2)
            
            if current_group:
                similar_groups.append(current_group)
                processed_images.add(img1)
    
    return similar_groups

def show_sample_similars(similar_groups):
    """Hiển thị một cặp ảnh mẫu từ nhóm ảnh tương tự đầu tiên"""
    if not similar_groups:
        return None
        
    first_group = similar_groups[0]
    img_path1 = first_group[0]  # Ảnh gốc
    img_path2 = first_group[1]  # Ảnh tương tự đầu tiên
    
    img1 = cv2.imread(str(img_path1))
    img2 = cv2.imread(str(img_path2))
    
    if img1 is None or img2 is None:
        return None
    
    # Đảm bảo ảnh có cùng kích thước để hiển thị
    height = 400
    width1 = int(img1.shape[1] * height / img1.shape[0])
    width2 = int(img2.shape[1] * height / img2.shape[0])
    
    img1 = cv2.resize(img1, (width1, height))
    img2 = cv2.resize(img2, (width2, height))
    
    # Hiển thị tên file trên ảnh
    cv2.putText(img1, img_path1.name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(img2, img_path2.name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Ghép 2 ảnh ngang nhau
    combined = np.hstack((img1, img2))
    
    window_name = 'Ảnh tương tự - Nhấn c để xóa TẤT CẢ ảnh tương tự, phím khác để thoát'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, combined)
    return cv2.waitKey(0) & 0xFF

def delete_all_similars(similar_groups):
    """Xóa tất cả ảnh tương tự (giữ lại ảnh đầu tiên của mỗi nhóm)"""
    deleted_count = 0
    for group in similar_groups:
        original = group[0]  # Giữ lại ảnh đầu tiên
        similars_to_remove = group[1:]  # Xóa các ảnh còn lại
        
        for img_path in similars_to_remove:
            try:
                os.remove(img_path)
                print(f"Đã xóa: {img_path.name}")
                deleted_count += 1
            except Exception as e:
                print(f"Lỗi khi xóa {img_path.name}: {e}")
    
    return deleted_count

def main():
    folder_path = Path("smoke detection1.v3i.yolov11\y\images")
    
    if not folder_path.exists():
        print(f"Thư mục {folder_path} không tồn tại!")
        return
    
    print("Đang tìm ảnh tương tự...")
    similar_groups = find_similar_images(folder_path, similarity_threshold=85)
    
    if not similar_groups:
        print("Không tìm thấy ảnh tương tự!")
        return
    
    # Tính tổng số ảnh tương tự
    total_similars = sum(len(group) - 1 for group in similar_groups)
    print(f"\nTìm thấy {total_similars} ảnh tương tự trong {len(similar_groups)} nhóm")
    
    # Hiển thị một cặp ảnh mẫu và chờ xác nhận
    if show_sample_similars(similar_groups) == ord('c'):
        print("\nĐang xóa tất cả ảnh tương tự...")
        deleted_count = delete_all_similars(similar_groups)
        print(f"\nĐã xóa thành công {deleted_count} ảnh tương tự")
    else:
        print("\nĐã hủy thao tác xóa")
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()