# Create Project

---

**English**

A Tkinter-based GUI tool for quickly scaffolding new projects. Select a project type, fill in the required fields, and the tool generates the project structure along with a `guidance.txt` containing useful commands.

---

**Tiếng Việt**

Công cụ giao diện Tkinter dùng để tạo nhanh các dự án mới. Chọn loại dự án, điền các trường bắt buộc, công cụ sẽ tạo cấu trúc dự án kèm file `guidance.txt` chứa các lệnh hướng dẫn sử dụng.

---

## Supported Project Types / Loại dự án hỗ trợ

| Loại | Công cụ | Mô tả |
|------|---------|-------|
| Maven | `mvn archetype:generate` | Dự án Java library với JUnit 5 |
| Gradle | `gradle init` | Dự án Java library với Groovy hoặc Kotlin DSL |
| NestJS | `@nestjs/cli` | Framework backend TypeScript (Node.js) |
| NextJS | `create-next-app` | Framework React full-stack |
| Android | Python file generator | Skeleton Android app với AGP, Kotlin hoặc Java |

## Requirements / Yêu cầu

- Python 3.13+
- Dự án Maven/Gradle: cài đặt `mvn` và/hoặc `gradle` trong `PATH`
- Dự án NestJS/NextJS: cài đặt Node.js
- Dự án Android: JDK 17+, Android SDK, và biến môi trường `ANDROID_HOME`
- PyInstaller (để build file `.exe`)

## Usage / Cách dùng

```bash
python main.py
```

Cửa sổ GUI sẽ mở ra. Chọn loại dự án từ dropdown, điền thông tin cần thiết rồi nhấn Submit.

## Build Distribution / Build bản phân phối

```bash
pyinstaller main.spec --noconfirm
```

File thực thi sẽ được tạo tại `dist/main.exe`.

## Project Structure / Cấu trúc dự án

```
create-project/
├── main.py                  # Entry point / Điểm vào
├── main.spec                # PyInstaller spec
├── registry.py              # ánh xạ loại dự án sang command class
├── views/
│   ├── view.py              # Abstract View base class / Lớp trừu tượng View
│   └── tkinter_view.py      # Tkinter GUI implementation / Triển khai giao diện Tkinter
└── commands/
    ├── cmd.py               # Abstract Command base class / Lớp trừu tượng Command
    ├── maven.py              # Maven scaffolding
    ├── gradle.py             # Gradle scaffolding
    ├── nestjs.py             # NestJS scaffolding
    ├── nextjs.py             # Next.js scaffolding
    └── android.py            # Android scaffolding
```

## Adding a New Project Type / Thêm loại dự án mới

**1. Tạo file mới trong `commands/` kế thừa `Cmd`:**

**English:** Create a new file in `commands/` extending `Cmd`:

**Tiếng Việt:** Tạo file mới trong `commands/`, kế thừa class `Cmd`:

```python
from commands.cmd import Cmd
from typing import override

class MyFramework(Cmd):
    def __init__(self):
        super().__init__()

    @override
    @property
    def requirements(self):
        return {
            "project_name": {
                "type": "str",
                "prompt": "Enter the project name:",
                "required": True
            }
        }

    @override
    @property
    def readme(self):
        return "Usage notes written to guidance.txt"

    @override
    @property
    def command(self):
        return f"your-cli create {self.user_input.get('project_name', '')}"
```

**2. Đăng ký trong `registry.py`:**

**English:** Register it in `registry.py`:

**Tiếng Việt:** Đăng ký trong `registry.py`:

```python
from commands import myframework

self.fields = {
    ...,
    "MyFramework": myframework.MyFramework
}
```

## License

MIT
