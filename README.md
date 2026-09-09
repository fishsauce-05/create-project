# Create-Project

## English

Create-Project is a Python desktop tool (Tkinter) that helps you quickly scaffold common project types from a simple UI.

### Features
- Select project type from the UI
- Fill required inputs and run setup commands automatically
- Generate a `guidance.txt` file inside the created project with useful notes

### Supported project types
- Maven
- Gradle
- NestJS
- NextJS

### Requirements
- Python 3.10+ (for `match` syntax)
- Tools installed based on project type:
  - Maven (`mvn`)
  - Gradle (`gradle`)
  - Node.js + npm + npx (for NestJS/NextJS)

### Run
From the repository root:

```bash
python main.py [target_directory]
```

- `target_directory` is optional.
- If omitted, projects are created in the current directory.

### How it works
1. Launches UI
2. Choose project type
3. Enter required fields
4. Runs related scaffold command
5. Writes project guidance to `guidance.txt`

---

## Tiếng Việt

Create-Project là công cụ desktop viết bằng Python (Tkinter), giúp bạn tạo nhanh các loại project phổ biến thông qua giao diện đơn giản.

### Tính năng
- Chọn loại project trên giao diện
- Nhập thông tin bắt buộc và tự động chạy lệnh khởi tạo
- Tạo file `guidance.txt` trong project mới để hướng dẫn sử dụng

### Các loại project hỗ trợ
- Maven
- Gradle
- NestJS
- NextJS

### Yêu cầu
- Python 3.10+ (để dùng cú pháp `match`)
- Cài sẵn công cụ theo từng loại project:
  - Maven (`mvn`)
  - Gradle (`gradle`)
  - Node.js + npm + npx (cho NestJS/NextJS)

### Cách chạy
Tại thư mục gốc repository:

```bash
python main.py [thu_muc_dich]
```

- `thu_muc_dich` là tùy chọn.
- Nếu không truyền, project sẽ được tạo trong thư mục hiện tại.

### Luồng hoạt động
1. Mở giao diện
2. Chọn loại project
3. Nhập thông tin yêu cầu
4. Chạy lệnh khởi tạo tương ứng
5. Ghi hướng dẫn vào file `guidance.txt`
