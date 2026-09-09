from commands.cmd import Cmd
from typing import override

class Nextjs(Cmd):
    def __init__(self):
        super().__init__()
        self.project_name = self.user_input.get("project_name", "")
        
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
        return """
        Next.js - Note

        1. Chạy development
        • Chạy server và tự reload khi sửa code: npm run dev
        • Mặc định mở tại http://localhost:3000
        • Đổi port (ví dụ sang cổng 4000): npm run dev -- -p 4000

        2. Build và chạy production
        • Tạo bản production: npm run build
        • Chạy bản đã build: npm run start
        • Luôn chạy build trước start; npm run start không thay thế npm run dev.
        • Xóa output build thủ công nếu cần: xóa thư mục .next.

        3. Cấu trúc thường gặp
        • app/: App Router, layout, page, loading, error và route handlers.
        • pages/: Pages Router cũ, chỉ dùng khi project chọn cấu trúc này.
        • public/: File tĩnh, truy cập từ root URL.
        • next.config.*: Cấu hình Next.js.
        • Các component dùng state, event hoặc browser API cần có 'use client'.

        4. Lint và format
        • Chạy lint: npm run lint
        • Script lint được tạo sẵn tùy phiên bản create-next-app; kiểm tra package.json nếu lệnh không có.
        • Có thể thêm Prettier để format code và tạo script "format" trong package.json.

        5. Test
        Next.js không mặc định tạo script test. Chọn công cụ phù hợp rồi thêm vào package.json:
            "scripts": {
                "test": "jest",
                "test:watch": "jest --watch",
                "test:e2e": "playwright test"
            }
        • Unit/component test: Jest hoặc Vitest.
        • End-to-end test: Playwright hoặc Cypress.
        • Cài dependency và cấu hình test runner trước khi chạy npm run test.

        6. Biến môi trường
        • Biến chỉ dùng phía server đặt trong .env.local, ví dụ: DATABASE_URL=...
        • Biến cần dùng ở client phải có tiền tố NEXT_PUBLIC_, ví dụ NEXT_PUBLIC_API_URL=...
        • Không đặt secret vào biến NEXT_PUBLIC_ vì giá trị này có thể xuất hiện trong bundle client.
        • Không commit file .env.local; nên tạo .env.example để mô tả các biến cần có.

        7. Dọn sạch và build lại
        • Xóa .next rồi build: npm run clean && npm run build
        • Next.js không luôn tạo sẵn script clean. Nếu cần, cài rimraf:
            npm install --save-dev rimraf
        • Thêm vào package.json:
            "scripts": {
                "clean": "rimraf .next",
                "build": "next build",
                "start": "next start"
            }
        """
        
    @override
    @property
    def command(self):
        project_name = self.user_input.get("project_name", "")
        return (
            f'npx --yes create-next-app@latest {project_name} --yes'
        )