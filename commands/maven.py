from commands.cmd import Cmd
from typing import override

class Maven(Cmd):
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
            "package_name": {
                "type": "str",
                "prompt": "Enter the package name (default = com.example):",
                "required": False
            }
        }
    
    @override
    @property
    def readme(self):
        return """
        Maven - Note

        1. Compile, test và đóng gói
        • Compile source: mvn compile
        • Chạy test: mvn test
        • Đóng gói JAR và chạy toàn bộ verify: mvn package
        • Xóa output target: mvn clean
        • Dọn sạch rồi build/test lại: mvn clean verify
        • File JAR nằm trong target.

        2. Chạy ứng dụng Java
        Maven Quickstart không cấu hình sẵn exec-maven-plugin. Thêm plugin sau vào pom.xml:
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.codehaus.mojo</groupId>
                        <artifactId>exec-maven-plugin</artifactId>
                        <version>3.5.0</version>
                        <configuration>
                            <mainClass>com.example.App</mainClass>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        • Chạy trực tiếp: mvn compile exec:java
        • Có thể truyền class khác: mvn compile exec:java -Dexec.mainClass="com.example.App"
        • Class main cần có public static void main(String[] args).

        3. Dependency và test JUnit
        • Thêm dependency test vào pom.xml nếu project chưa có:
            <dependency>
                <groupId>org.junit.jupiter</groupId>
                <artifactId>junit-jupiter</artifactId>
                <version>5.12.2</version>
                <scope>test</scope>
            </dependency>
        • Test mặc định thường nằm trong src/test/java và tên class kết thúc bằng Test.
        • Bỏ qua test khi build: mvn package -DskipTests
        • Chạy lại cả clean, compile và test: mvn clean compile test

        4. Dependency và thông tin project
        • Xem dependency tree: mvn dependency:tree
        • Kiểm tra cấu hình effective POM: mvn help:effective-pom
        • Maven Wrapper (nếu có): mvnw.cmd <goal> trên Windows hoặc ./mvnw <goal> trên Linux/macOS.

        5. Đóng gói WAR
        • Thêm <packaging>war</packaging> vào pom.xml nếu triển khai lên servlet container.
        • JAR phù hợp để chạy như ứng dụng độc lập; WAR phù hợp với server/container hỗ trợ WAR.
        """
    
    @override
    @property
    def command(self):
        project_name = self.user_input.get("project_name")
        package_name = self.user_input.get("package_name", "com.example")
        return (
            f'mvn archetype:generate'
            f' -DgroupId={package_name}'
            f' -DartifactId={project_name}'
            f' -DarchetypeArtifactId=maven-archetype-quickstart'
            f' -DinteractiveMode=false'
        )