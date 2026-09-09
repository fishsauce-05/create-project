from commands.cmd import Cmd
from typing import override

class Nest(Cmd):
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
        return """
        NestJS - Note

        1. Chạy ứng dụng
        Chạy thông thường: npm run start
        Chạy development, tự động build lại khi sửa code: npm run start:dev
        Ứng dụng mặc định chạy tại http://localhost:3000
        
        2. Build và chạy production
        Build: npm run build
        Chạy bản đã build: npm run start:prod
        Dùng biến môi trường PORT để đổi cổng chạy ứng dụng.
        
        3. Tạo thành phần bằng Nest CLI
        • nest g module users
        • nest g controller users
        • nest g service users
        • nest g resource users (tạo nhanh bộ CRUD)
        
        4. Test, lint và format
        • Unit test: npm run test
        • Lint: npm run lint
        • Format: npm run format
        • Theo dõi unit test: npm run test:watch
        • Báo cáo coverage: npm run test:cov
        • End-to-end test: npm run test:e2e
        • Lint: npm run lint
        • Format: npm run format
        
        5. Cấu hình biến môi trường
        • Cài package: npm i @nestjs/config
        • Thêm ConfigModule.forRoot() vào AppModule để đọc file .env.
        • Dùng ConfigService để đọc giá trị, ví dụ: configService.get('PORT').
        • Có thể đặt isGlobal: true nếu muốn dùng ConfigService trong nhiều module.
        
        6. Validate request
        • Cài package: npm i class-validator class-transformer
        • Bật toàn cục trong src/main.ts:
            app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }))
        • Dùng DTO class với các decorator như @IsEmail(), @IsNotEmpty(), @IsInt().
        • whitelist sẽ loại bỏ field không được khai báo trong DTO.
        """

    @override
    @property
    def command(self):
        project_name = self.user_input.get("project_name", "")
        return (
            f'set "CI=true" & npx --yes @nestjs/cli new {project_name}'
            f' --package-manager npm'
            f' --no-observe'
        )