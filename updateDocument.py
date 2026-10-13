import os
import json
from google.cloud import firestore

# Tự động lấy đường dẫn tuyệt đối của thư mục chứa file code hiện tại
current_dir = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn tự động trỏ đến các file nằm cùng thư mục
credential_path = os.path.join(current_dir, "serviceAccountKey.json")
data_json_path = os.path.join(current_dir, "update_data.json")

# Thiết lập xác thực Google Cloud / Firebase
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path


def load_update_data():
    if not os.path.exists(data_json_path):
        raise FileNotFoundError(
            f"Không tìm thấy file 'update_data.json' trong cùng thư mục tại đường dẫn:\n{data_json_path}"
        )

    with open(data_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_store_documents(db, collection_name="stores"):
    docs = db.collection(collection_name).stream()
    document_ids = [doc.id for doc in docs]
    return sorted(document_ids)


def choose_document_id(document_ids):
    if not document_ids:
        print("Không có document nào trong collection 'stores'.")
        return None

    print("\nDanh sách cửa hàng:")
    for index, doc_id in enumerate(document_ids, start=1):
        print(f"  {index}. {doc_id}")

    while True:
        user_input = input("\nChọn số tương ứng với cửa hàng cần cập nhật (hoặc nhấn Enter để thoát): ").strip()

        if user_input == "":
            print("Đã hủy thao tác cập nhật.")
            return None

        try:
            selected_index = int(user_input)
        except ValueError:
            print("Vui lòng nhập số hợp lệ.")
            continue

        if 1 <= selected_index <= len(document_ids):
            return document_ids[selected_index - 1]

        print(f"Số bạn nhập không hợp lệ. Chỉ chấp nhận từ 1 đến {len(document_ids)}.")


def choose_week_key(doc_ref):
    doc_snapshot = doc_ref.get()
    if not doc_snapshot.exists:
        print("Store không tồn tại.")
        return None

    data = doc_snapshot.to_dict() or {}
    weeks = data.get("weeks", {})
    week_keys = list(weeks.keys()) if isinstance(weeks, dict) else []
    week_keys = sorted(week_keys)

    if not week_keys:
        print("Cửa hàng này chưa có dữ liệu tuần.")
        return None

    print("\nDanh sách tuần:")
    for index, key in enumerate(week_keys, start=1):
        print(f"  {index}. {key}")

    while True:
        user_input = input("\nChọn số tuần cần cập nhật: ").strip()

        if user_input == "":
            print("Đã hủy thao tác cập nhật.")
            return None

        try:
            selected_index = int(user_input)
        except ValueError:
            print("Vui lòng nhập số hợp lệ.")
            continue

        if 1 <= selected_index <= len(week_keys):
            return week_keys[selected_index - 1]

        print(f"Số không hợp lệ. Chỉ chấp nhận từ 1 đến {len(week_keys)}.")


def connect_and_update_firestore():
    try:
        # 1. Khởi tạo kết nối tới Firestore
        db = firestore.Client()
        print("Kết nối thành công đến Firestore!")

        # 2. Tải dữ liệu cần cập nhật từ file JSON
        from_data = load_update_data()

        # 3. Lấy danh sách store trong collection stores
        collection_name = "stores"
        document_ids = list_store_documents(db, collection_name)

        # 4. Cho phép người dùng chọn store từ console
        selected_document_id = choose_document_id(document_ids)
        if selected_document_id is None:
            return

        # 5. Chọn key weeks cụ thể trong document đó để update
        doc_ref = db.collection(collection_name).document(selected_document_id)
        selected_week_key = choose_week_key(doc_ref)
        if selected_week_key is None:
            return

        6. Cập nhật dữ liệu vào document & key được chọn
        doc_ref.set({
            "weeks": {
                selected_week_key: from_data
            }
        }, merge=True)

        print(f"\nĐã cập nhật thành công dữ liệu cho store: {selected_document_id}, tuần: {selected_week_key}")

    except FileNotFoundError as e:
        print(f"Lỗi: {e}")
    except Exception as e:
        print(f"Lỗi kết nối hoặc cập nhật Firestore: {e}")


if __name__ == "__main__":
    connect_and_update_firestore()