package com.terrasoft.contratista

import android.util.Base64
import android.util.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.terrasoft.contratista/fingerprint"
    private val TAG = "MainActivity"
    private var fingerprintReader: UsbFingerprintReader? = null
    
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        fingerprintReader = UsbFingerprintReader(this)
        
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "checkDevice" -> {
                        val found = fingerprintReader?.checkDevice() ?: false
                        result.success(found)
                    }
                    "scanFingerprint" -> {
                        scanFingerprint(result)
                    }
                    else -> {
                        result.notImplemented()
                    }
                }
            }
    }
    
    private fun scanFingerprint(result: MethodChannel.Result) {
        try {
            if (fingerprintReader?.connect() == true) {
                val data = fingerprintReader?.captureFingerprint()
                
                if (data != null) {
                    val base64 = Base64.encodeToString(data, Base64.NO_WRAP)
                    result.success(base64)
                } else {
                    result.error("NO_DATA", "No data captured", null)
                }
                
                fingerprintReader?.disconnect()
            } else {
                result.error("CONNECTION_ERROR", "Failed to connect", null)
            }
        } catch (e: Exception) {
            result.error("EXCEPTION", e.message, null)
        }
    }
}