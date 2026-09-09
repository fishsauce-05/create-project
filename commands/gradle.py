from commands.cmd import Cmd
from typing import override

class Gradle(Cmd):
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
            },
            "dsl": {
                "type": "radio",
                "prompt": "Choose the DSL for Gradle:",
                "option": ["groovy", "kotlin"],
                "required": True
            }
        }
    
    @override
    @property
    def readme(self):
        return """
        Gradle - Note

        • Gradle dùng phiên bản được cài trên máy
        • Gradle Wrapper (gradlew/gradlew.bat) dùng đúng phiên bản đã ghi trong dự án và tự tải phiên bản đó nếu cần.
        => Nên ưu tiên Wrapper để mọi máy và CI dùng cùng một phiên bản Gradle.

        1. Build và kiểm tra project
        • Windows: gradlew.bat build
        • Linux/macOS: ./gradlew build
        • Build gồm compile, test và các bước kiểm tra được khai báo trong build.gradle.
        • Xóa output build: gradlew.bat clean

        2. Chạy ứng dụng
        • Project được tạo bởi command này là java-library nên không có task run mặc định.
        • Nếu đây là ứng dụng Java, thêm plugin application vào build.gradle:
            plugins {
                id 'application'
            }
            application {
                mainClass = 'org.example.App'
            }
        • Chạy ứng dụng: gradlew.bat run hoặc ./gradlew run
        • mainClass phải có hàm main(String[] args).

        3. Chạy test
        • Chạy test: gradlew.bat test hoặc ./gradlew test
        • Với JUnit 5, khai báo dependency và bật nền tảng JUnit:
            dependencies {
                testImplementation 'org.junit.jupiter:junit•jupiter:5.10.2'
            }
            test {
                useJUnitPlatform()
            }
        • Xem báo cáo test: build/reports/tests/test/index.html

        4. Task và dependency
        • Liệt kê task: gradlew.bat tasks hoặc ./gradlew tasks
        • Xem dependency: gradlew.bat dependencies hoặc ./gradlew dependencies
        • Chạy một task cụ thể: gradlew.bat <task-name>

        5. Đóng gói
        • Tạo JAR: gradlew.bat jar hoặc ./gradlew jar
        • Nếu tạo web application, thêm plugin:
            plugins {
                id 'war'
            }
        • Tạo WAR: gradlew.bat war hoặc ./gradlew war
        • File đầu ra nằm trong thư mục build/libs.

        6. Quy trình thường dùng
        • Dọn sạch, build và test lại: gradlew.bat clean build
        • Không cần cài Gradle toàn cục nếu dự án đã có Gradle Wrapper.
        """
    
    @override
    @property
    def command(self):
        project_name = self.user_input.get("project_name", "")
        dsl = self.user_input.get("dsl", "groovy")
        return (
            f'mkdir {project_name} && cd {project_name} && gradle init'
            f' --type java-library'
            f' --dsl {dsl}'
            f' --test-framework junit-jupiter'
            f' --project-name {project_name}'
            f' --no-split-project'
            f' --java-version 21'
            f' --overwrite'
            f' --no-incubating'
        )