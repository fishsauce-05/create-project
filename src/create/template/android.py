from ._base import CreateProjectByTemplate
from typing import override
import os
import platform
from pathlib import Path

DEFAULT_PACKAGE = "com.fishsauce.app"
DEFAULT_APP_NAME = "Fishsauce"
DEFAULT_DISPLAY_TEXT = "Hello Fishsauce"

class Android(CreateProjectByTemplate):
    def __init__(self):
        super().__init__()
        
    @override
    @property
    def requirements(self):
        return {
            "project_name": {
                "type": "str",
                "prompt": "Enter the project name",
                "name": "project name",
                "required": True
            },
            "package_name": {
                "type": "str",
                "prompt": f"Enter the package name (default: {DEFAULT_PACKAGE})",
                "default": DEFAULT_PACKAGE,
                "required": False
            },
            "application_name": {
                "type": "str", 
                "prompt": f"Enter the applicatoin name (default: {DEFAULT_APP_NAME})",
                "default": DEFAULT_APP_NAME,
                "required": False
            },
            "sdk_directory": {
                "type": "str",
                "prompt": "Enter the Android SDK directory",
                "default": self.__get_android_sdk_directory(),
                "required": False
            }
        }
    
    def __get_android_sdk_directory(self):
        android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
        if android_home:
            sdk_path = Path(android_home).as_posix()
            return sdk_path
        
        home_dir = Path.home()
        system = platform.system()
        match (system):
            case "Windows":
                return Path(home_dir / "AppData" / "Local" / "Android" / "Sdk").as_posix()
            case "Darwin":
                return Path(home_dir / "Library" / "Android" / "sdk").as_posix()
            case "Linux":
                return Path(home_dir / "Android" / "Sdk").as_posix()
            case _:
                return ""

    @override
    @property
    def readme(self):
        return """
        Android - Note
        
        1. Build và kiểm tra project
        • Windows: gradlew.bat build
        • Linux/macOS: ./gradlew build
        • Build gồm compile, test và các bước kiểm tra được khai báo trong build.gradle.
        • Xóa output build: gradlew.bat clean
        2. Chạy ứng dụng
        • Cần phải thêm cái adb và emulator vào PATH để chạy lệnh adb từ terminal.
        • Chạy ứng dụng: gradlew.bat assembleDebug hoặc ./gradlew assembleDebug
        • File APK nằm trong app/build/outputs/apk/debug/app-debug.apk
        • Cài đặt APK lên thiết bị/emulator:
        - Khởi động thiết bị:
            - emulator: emulator -avd PIXEL_API_35 hoặc ./emulator -avd PIXEL_API_35
            - thiết bị thật: kết nối thiết bị qua USB và bật chế độ USB Debugging (Tự hỏi chat gpt nhé :'P)
        - Cài đặt APK: adb install -r app/build/outputs/apk/debug/app-debug.apk
        3. Chạy test
        • Chạy test: gradlew.bat test hoặc ./gradlew test
        """
        
    @override
    @property
    def template_path(self) -> Path:
        base_dir = super().template_path
        return base_dir / "android-studio"
    
    @override
    @property
    def renamed_dir(self) -> dict[str, str]:
        old_path = DEFAULT_PACKAGE.replace(".", "/")
        new_path = self.user_input.get("package_name", DEFAULT_PACKAGE).replace(".", "/")
        
        if old_path == new_path:
            return {}
        
        return {
            f"app/src/main/java/{old_path}": f"app/src/main/java/{new_path}",
            f"app/src/test/java/{old_path}": f"app/src/test/java/{new_path}",
            f"app/src/androidTest/java/{old_path}": f"app/src/androidTest/java/{new_path}",
        }
    
    @override
    @property
    def replaced_text(self) -> dict[str, str]:
        pkg_name = self.user_input.get("package_name", DEFAULT_PACKAGE)
        app_name = self.user_input.get("application_name", DEFAULT_APP_NAME)
        display_text = DEFAULT_DISPLAY_TEXT if app_name == DEFAULT_APP_NAME else app_name
        sdk_dir = self.user_input.get("sdk_directory", "")
        result = {
            DEFAULT_PACKAGE: pkg_name,
            DEFAULT_APP_NAME: app_name,
            DEFAULT_DISPLAY_TEXT: display_text,
            "sdk.dir=": f"sdk.dir={sdk_dir}"
        }
        if pkg_name == DEFAULT_PACKAGE:
            del result[DEFAULT_PACKAGE]
        if app_name == DEFAULT_APP_NAME:
            del result[DEFAULT_APP_NAME]
        if display_text == DEFAULT_DISPLAY_TEXT:
            del result[DEFAULT_DISPLAY_TEXT]
        return result
    
    @override
    @property
    def ignored_patterns(self) -> list[str]:
        return [
            ".gradle", ".gradle/*", "*/.gradle/*",
            "*.jar",
            "*.jks", "*.keystore",
            ".idea", ".idea/*"
        ]