# Fix JAVA_HOME for Android Studio's bundled JDK
# Run from your project folder

$androidStudio = "$env:LOCALAPPDATA\Programs\Android Studio"
$possibleJdks = @(
    "$androidStudio\jbr",
    "$androidStudio\jre",
    "C:\Program Files\Android\Android Studio\jbr",
    "C:\Program Files\Android\Android Studio\jre"
)

$jdkPath = $null
foreach ($p in $possibleJdks) {
    if (Test-Path "$p\bin\java.exe") {
        $jdkPath = $p
        break
    }
}

if ($jdkPath) {
    $env:JAVA_HOME = $jdkPath
    Write-Host "✅ JAVA_HOME set to: $jdkPath"
    Write-Host "Building now..."
    .\gradlew assembleDebug
} else {
    Write-Host "❌ Could not find Android Studio JDK automatically."
    Write-Host "Looking for java.exe..."
    Get-ChildItem "C:\Program Files\Android\Android Studio" -Recurse -Filter "java.exe" -ErrorAction SilentlyContinue | Select-Object -First 3 FullName
    Get-ChildItem "$env:LOCALAPPDATA\Programs\Android Studio" -Recurse -Filter "java.exe" -ErrorAction SilentlyContinue | Select-Object -First 3 FullName
}
