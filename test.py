from pathlib import Path

def print_folder_structure(path, indent=0):
    # In tên thư mục
    print(' ' * indent + '|-- ' + path.name)
    # Duyệt qua tất cả các mục trong thư mục
    for item in path.iterdir():
        if item.is_dir():
            print_folder_structure(item, indent + 4)  # Gọi đệ quy cho thư mục
        else:
            print(' ' * (indent + 4) + '|-- ' + item.name)  # In tên tệp

# Sử dụng hàm với đường dẫn đến thư mục gốc
print_folder_structure(Path('D:/Hoc_Hoang/EXE201/UpSale/apis'))
