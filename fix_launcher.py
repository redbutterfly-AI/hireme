import os

manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.HireMeApp"
        android:networkSecurityConfig="@xml/network_security_config">

        <!-- LAUNCHER: starts at MainActivity which checks login state -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity android:name=".LoginActivity"          android:exported="false" />
        <activity android:name=".RegisterActivity"       android:exported="false" />
        <activity android:name=".DashboardActivity"      android:exported="false" />
        <activity android:name=".JobsActivity"           android:exported="false" />
        <activity android:name=".JobDetailActivity"      android:exported="false" />
        <activity android:name=".PostJobActivity"        android:exported="false" />
        <activity android:name=".ApplicantsActivity"     android:exported="false" />
        <activity android:name=".ProfileActivity"        android:exported="false" />
        <activity android:name=".UploadCVActivity"       android:exported="false" />
        <activity android:name=".ChatActivity"           android:exported="false" />
        <activity android:name=".AdminDashboardActivity" android:exported="false" />
        <activity android:name=".EmployerDashboardActivity" android:exported="false" />
        <activity android:name=".EmployerJobsActivity"   android:exported="false" />
        <activity android:name=".NotificationActivity"   android:exported="false" />
        <activity android:name=".SeekersActivity"        android:exported="false" />
        <activity android:name=".MyApplicationsActivity" android:exported="false" />
        <activity android:name=".OTPVerificationActivity" android:exported="false" />

        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="com.example.hiremeapp.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>

    </application>
</manifest>
'''

path = os.path.join("app", "src", "main", "AndroidManifest.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(manifest)
print("✅ AndroidManifest.xml updated - MainActivity is now the launcher")
print("")
print("Now show me MainActivity.kt so we can make sure it redirects")
print("to LoginActivity if not logged in, or Dashboard if already logged in.")
