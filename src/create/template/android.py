from ._base import CreateProjectByTemplate
from typing import override
import os
import platform
from pathlib import Path

DEFAULT_PACKAGE = "com.fishsauce.app"
DEFAULT_APP_NAME = "Fishsauce and Cotton"

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
                "prompt": f"Enter the application name (default: {DEFAULT_APP_NAME})",
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
        Kotlin DSL (build.gradle.kts), compileSdk/targetSdk 37, minSdk 24, Java 11.
        Windows dùng gradlew.bat, Linux/macOS dùng ./gradlew (ghi tắt trong ví dụ bên dưới).

        1. Build và kiểm tra project
        • Build đầy đủ (compile + unit test + lint): ./gradlew build
        • Chỉ build APK debug, bỏ qua test/lint: ./gradlew assembleDebug
        • Chỉ chạy unit test: ./gradlew test
        • Chỉ chạy lint: ./gradlew lintDebug
        • Xóa output build: ./gradlew clean
        • Xem toàn bộ task: ./gradlew :app:tasks
        • Build nhanh hơn khi máy yếu: ./gradlew assembleDebug --no-daemon -Dorg.gradle.jvmargs=-Xmx1536m
        • Build offline (không tải dependency): ./gradlew assembleDebug --offline
        • Tải lại dependency: ./gradlew assembleDebug --refresh-dependencies
        • Trong gradle.properties đang bật org.gradle.configuration-cache=true.
        - Nếu build lỗi do configuration cache, thêm --no-configuration-cache.
        • Output nằm ở app/build.

        2. Chạy ứng dụng
        • Cài APK lên thiết bị đang kết nối (nhanh nhất): ./gradlew installDebug
        • Build rồi tự cài: ./gradlew assembleDebug
        • File APK: app/build/outputs/apk/debug/app-debug.apk
        • Cài APK có sẵn bằng tay: adb install -r app/build/outputs/apk/debug/app-debug.apk
        • Xem thiết bị đang kết nối: adb devices
        • Khởi động emulator: emulator -list-avds rồi emulator -avd <TEN_AVD>
        (trên Windows có thể chạy <SDK>/emulator/emulator.exe nếu chưa thêm vào PATH).
        • Thiết bị thật: cắm USB và bật USB Debugging trong Developer options.
        • Mở app: adb shell am start -n <package_name>/.MainActivity
        (dấu chấm = package hiện tại, không cần gói đầy đủ nếu Activity nằm ở root package).
        • Xem log của app: adb logcat --pid=$(adb shell pidof -s <package_name>)
        • Xem log toàn bộ: adb logcat -s ActivityManager AndroidRuntime
        • Dừng app: adb shell am force-stop <package_name>
        • Gỡ app: adb uninstall <package_name>

        3. Chạy test
        • Unit test (app/src/test/java) chạy trên JVM, không cần máy:
            ./gradlew test
            ./gradlew testDebugUnitTest
            ./gradlew test --tests "*ExampleUnitTest"     (chạy 1 class)
        • Thư viện test đang dùng: JUnit 4.13.2, Robolectric 4.11.1, androidx.test:core 1.5.0.
        - Robolectric chạy test Android API trên JVM, không cần emulator.
        - Test mới đặt trong app/src/test/java và dùng đúng package đã khai báo.
        • Instrumented test (app/src/androidTest/java) cần emulator hoặc máy thật:
            ./gradlew connectedDebugAndroidTest
            ./gradlew assembleDebugAndroidTest        (chỉ compile, không chạy)
        • Báo cáo test:
            Unit test HTML: app/build/reports/tests/testDebugUnitTest/index.html
            Unit test XML:  app/build/test-results/testDebugUnitTest/
            Instrumented:   app/build/reports/androidTests/connected/debug/index.html
        • Bỏ qua test khi build: ./gradlew assembleDebug -x test
        • Test fail vì code đổi mà test còn kỳ vọng giá trị cũ -> sửa lại assert cho khớp.

        4. Đóng gói bản release
        • Bản debug dùng signing config mặc định của AGP nên assembleDebug chạy được ngay.
        • Tạo keystore (không commit file này lên git):
            keytool -genkeypair -v -keystore release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias release
        • Khai báo signing trong app/build.gradle.kts:
            android {
                signingConfigs {
                    create("release") {
                        storeFile = file("release.jks")
                        storePassword = System.getenv("KEYSTORE_PASSWORD")
                        keyAlias = System.getenv("KEY_ALIAS")
                        keyPassword = System.getenv("KEY_PASSWORD")
                    }
                }
                buildTypes {
                    release {
                        signingConfig = signingConfigs.getByName("release")
                        isMinifyEnabled = true
                        isShrinkResources = true
                        proguardFiles(
                            getDefaultProguardFile("proguard-android-optimize.txt"),
                            "proguard-rules.pro"
                        )
                    }
                }
            }
        • Build và kiểm tra bản release: ./gradlew assembleRelease
        • Đóng gói AAB để upload lên Google Play: ./gradlew bundleRelease
        • Output:
            APK: app/build/outputs/apk/release/app-release.apk
            AAB: app/build/outputs/bundle/release/app-release.aab
        • File .jks / .keystore không bị công cụ sinh project đụng tới,
        nhưng vẫn nên để ngoài repo hoặc thêm vào .gitignore.
        • Rule cho R8 (giữ class không bênh vựng): app/src/main/keepRules/rules.keep
        (file mẫu đã có sẵn trong project).

        5. Chỉnh sửa nhanh
        • Mã nguồn: app/src/main/java/<đường dẫn package>/ (MainActivity, SayHelloActivity).
        • MainActivity đang dùng R.layout.home, gọi SayHelloActivity để chạy hiệu ứng gõ chữ.
        • Layout: app/src/main/res/layout/ (home.xml là layout đang chạy, activity_main.xml là mẫu).
        • Chuỗi hiển thị: app/src/main/res/values/strings.xml (app_name).
        • Theme: Theme.HelloApp trong values/themes.xml (Material3 DayNight NoActionBar),
        bản dark mode nằm ở values-night/themes.xml.
        • Đổi minSdk/targetSdk/compileSdk, applicationId, versionName: app/build.gradle.kts.
        • Đổi package thì phải sửa cả 3 chỗ:
            namespace + applicationId trong app/build.gradle.kts
            dòng package trong file .java
            thư mục app/src/{main,test,androidTest}/java/...
        • Dependency khai báo bằng alias trong gradle/libs.versions.toml, dùng trong build.gradle.kts
        dưới dạng libs.xxx.
        • Muốn bật ViewBinding: thêm viewBinding = true trong android { } của app/build.gradle.kts.

        6. Khi build lỗi
        • Lỗi SDK location not found: kiểm tra sdk.dir trong local.properties hoặc ANDROID_HOME.
        • Lỗi dependency: ./gradlew clean rồi build lại; vẫn lỗi thì xóa .gradle/ và build/.
        • Lỗi do daemon cũ: ./gradlew --stop rồi build lại.
        • Lỗi sau khi đổi package mà file cũ còn sót: ./gradlew clean assembleDebug.
        • Xem đầy đủ lỗi: ./gradlew assembleDebug --stacktrace --info.
        • Kiểm tra cấu hình Gradle đang dùng: ./gradlew -q javaToolchains, ./gradlew -v.
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
        sdk_dir = self.user_input.get("sdk_directory", "").strip().replace("\\", "/")
        result = {
            DEFAULT_PACKAGE: pkg_name,
            DEFAULT_APP_NAME: app_name
        }
        if pkg_name == DEFAULT_PACKAGE:
            del result[DEFAULT_PACKAGE]
        if app_name == DEFAULT_APP_NAME:
            del result[DEFAULT_APP_NAME]
        return result
    
    @override
    @property
    def ignored_patterns(self):
        return [
            ".gradle", ".gradle/*", "*/.gradle/*",
            "*.jar",
            "*.jks", "*.keystore",
            ".idea", ".idea/*"
        ]

    @override
    @property
    def new_files(self):
        project_name = self.user_input.get("project_name", "")
        project_dir = self.project_path / project_name / "local.properties"
        sdk_dir = self.user_input.get("sdk_directory", "").strip()

        return {
            Path(project_dir): f"sdk.dir = {sdk_dir}"
        }