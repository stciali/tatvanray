import os
import sys
import re

GOOGLE_MAVEN_MIRROR_KTS = 'maven { url = uri("https://maven-central.storage-download.googleapis.com/maven2/") }'
GOOGLE_MAVEN_MIRROR_GROOVY = "maven { url 'https://maven-central.storage-download.googleapis.com/maven2/' }"

def patch_settings_gradle():
    kts_path = os.path.join("android", "settings.gradle.kts")
    groovy_path = os.path.join("android", "settings.gradle")

    if os.path.exists(kts_path):
        with open(kts_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "maven-central.storage-download.googleapis.com" not in content:
            content = re.sub(
                r"(repositories\s*\{)",
                r"\1\n        google()\n        " + GOOGLE_MAVEN_MIRROR_KTS,
                content
            )
            with open(kts_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Injected Google Maven mirror into {kts_path}")

    if os.path.exists(groovy_path):
        with open(groovy_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "maven-central.storage-download.googleapis.com" not in content:
            content = re.sub(
                r"(repositories\s*\{)",
                r"\1\n        google()\n        " + GOOGLE_MAVEN_MIRROR_GROOVY,
                content
            )
            with open(groovy_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Injected Google Maven mirror into {groovy_path}")

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

    aar_bypass_kts = (
        '\nsubprojects {\n'
        '    tasks.configureEach {\n'
        '        if (name.contains("AarMetadata", ignoreCase = true)) {\n'
        '            enabled = false\n'
        '        }\n'
        '    }\n'
        '}\n'
    )

    aar_bypass_groovy = (
        '\nsubprojects {\n'
        '    tasks.configureEach { task ->\n'
        '        if (task.name.contains("AarMetadata")) {\n'
        '            task.enabled = false\n'
        '        }\n'
        '    }\n'
        '}\n'
    )

    if os.path.exists(root_kts):
        with open(root_kts, "r", encoding="utf-8") as f:
            content = f.read()

        if "maven-central.storage-download.googleapis.com" not in content:
            content = re.sub(
                r"(repositories\s*\{)",
                r"\1\n        google()\n        " + GOOGLE_MAVEN_MIRROR_KTS,
                content
            )

        if "AarMetadata" not in content:
            content += aar_bypass_kts

        with open(root_kts, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched: {root_kts}")

    if os.path.exists(root_groovy):
        with open(root_groovy, "r", encoding="utf-8") as f:
            content = f.read()

        if "maven-central.storage-download.googleapis.com" not in content:
            content = re.sub(
                r"(repositories\s*\{)",
                r"\1\n        google()\n        " + GOOGLE_MAVEN_MIRROR_GROOVY,
                content
            )

        if "AarMetadata" not in content:
            content += aar_bypass_groovy

        with open(root_groovy, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched: {root_groovy}")

def patch_gradle_properties():
    props_path = os.path.join("android", "gradle.properties")
    if os.path.exists(props_path):
        with open(props_path, "a", encoding="utf-8") as f:
            f.write(
                "\n"
                "systemProp.org.gradle.internal.http.connectionTimeout=60000\n"
                "systemProp.org.gradle.internal.http.socketTimeout=60000\n"
            )
        print(f"Patched: {props_path}")

def patch_pub_cache():
    home = os.path.expanduser("~")
    pub_cache = os.path.join(home, ".pub-cache")
    if not os.path.exists(pub_cache):
        print(f"Pub cache directory not found: {pub_cache}")
        return

    count = 0
    for root, dirs, files in os.walk(pub_cache):
        for f in files:
            if f in ("build.gradle", "build.gradle.kts"):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, "r", encoding="utf-8") as fp:
                        content = fp.read()
                    new_content = re.sub(r'compileSdkVersion\s+3[0-5]', 'compileSdkVersion 36', content)
                    new_content = re.sub(r'compileSdk\s*=\s*3[0-5]', 'compileSdk = 36', new_content)
                    new_content = re.sub(r'compileSdkVersion\s*=\s*3[0-5]', 'compileSdkVersion = 36', new_content)
                    if new_content != content:
                        with open(fpath, "w", encoding="utf-8") as fp:
                            fp.write(new_content)
                        count += 1
                except Exception:
                    pass
    print(f"Patched {count} plugin files in pub cache to compileSdk 36.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--pub-cache":
        patch_pub_cache()
    else:
        patch_settings_gradle()
        patch_app_gradle()
        patch_root_gradle()
        patch_gradle_properties()
        print("All Gradle configurations and AarMetadata bypass applied.")
