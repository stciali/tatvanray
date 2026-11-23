import os
import re

def patch_app_gradle():
    app_kts = os.path.join("android", "app", "build.gradle.kts")
    app_groovy = os.path.join("android", "app", "build.gradle")

    if os.path.exists(app_kts):
        with open(app_kts, "r", encoding="utf-8") as f:
            content = f.read()

        # Bump compileSdk, minSdk, targetSdk
        content = re.sub(r"compileSdk\s*=\s*flutter\.compileSdkVersion", "compileSdk = 36", content)
        content = re.sub(r"minSdk\s*=\s*flutter\.minSdkVersion", "minSdk = 21", content)
        content = re.sub(r"targetSdk\s*=\s*flutter\.targetSdkVersion", "targetSdk = 34", content)

        # Configure release build type with minification disabled
        if "isMinifyEnabled" not in content:
            release_block = (
                "release {\n"
                "            isMinifyEnabled = false\n"
                "            isShrinkResources = false\n"
                '            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")\n'
            )
            content = re.sub(r"release\s*\{", release_block, content, count=1)

        with open(app_kts, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched: {app_kts}")

    if os.path.exists(app_groovy):
        with open(app_groovy, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(r"compileSdkVersion\s+flutter\.compileSdkVersion", "compileSdkVersion 36", content)
        content = re.sub(r"minSdkVersion\s+flutter\.minSdkVersion", "minSdkVersion 21", content)
        content = re.sub(r"targetSdkVersion\s+flutter\.targetSdkVersion", "targetSdkVersion 34", content)

        if "minifyEnabled" not in content:
            release_block = (
                "release {\n"
                "            minifyEnabled false\n"
                "            shrinkResources false\n"
                '            proguardFiles getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro"\n'
            )
            content = re.sub(r"release\s*\{", release_block, content, count=1)

        with open(app_groovy, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched: {app_groovy}")

def patch_root_gradle():
    root_kts = os.path.join("android", "build.gradle.kts")
    root_groovy = os.path.join("android", "build.gradle")

    if os.path.exists(root_kts):
        with open(root_kts, "a", encoding="utf-8") as f:
            f.write(
                "\n"
                "subprojects {\n"
                "    afterEvaluate {\n"
                '        if (project.hasProperty("android")) {\n'
                '            val android = project.extensions.findByName("android")\n'
                "            if (android != null) {\n"
                "                try {\n"
                '                    val method = android::class.java.getMethod("compileSdkVersion", Int::class.javaPrimitiveType)\n'
                "                    method.invoke(android, 36)\n"
                "                } catch (e: Exception) {\n"
                "                }\n"
                "            }\n"
                "        }\n"
                "    }\n"
                "}\n"
            )
        print(f"Patched: {root_kts}")

    if os.path.exists(root_groovy):
        with open(root_groovy, "a", encoding="utf-8") as f:
            f.write(
                "\n"
                "subprojects {\n"
                "    afterEvaluate { project ->\n"
                '        if (project.hasProperty("android")) {\n'
                "            android {\n"
                "                compileSdkVersion 36\n"
                "            }\n"
                "        }\n"
                "    }\n"
                "}\n"
            )
        print(f"Patched: {root_groovy}")

if __name__ == "__main__":
    patch_app_gradle()
    patch_root_gradle()
    print("Gradle configuration complete.")
