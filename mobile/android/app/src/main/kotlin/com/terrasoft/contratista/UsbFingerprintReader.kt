package com.terrasoft.contratista

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Color
import android.hardware.usb.*
import android.util.Log
import com.synochip.sdk.ukey.OTG_KEY
import java.io.ByteArrayOutputStream

class UsbFingerprintReader(private val context: Context) {
    
    private val TAG = "UsbFingerprintReader"
    private var usbDevice: UsbDevice? = null
    private var otgKey: OTG_KEY? = null
    private var usbManager: UsbManager? = null
    
    companion object {
        const val VENDOR_ID = 17938  // 0x4612
        const val PRODUCT_ID = 1204  // 0x04b4
        
        const val DEV_ADDR = 0xffffffff.toInt()
        const val IMAGE_WIDTH = 256
        const val IMAGE_HEIGHT = 288
        const val PS_OK = 0x00
        const val PS_NO_FINGER = 0x02
        const val DEVICE_SUCCESS = 0
    }
    
    fun checkDevice(): Boolean {
        try {
            usbManager = context.getSystemService(Context.USB_SERVICE) as UsbManager
            val deviceList = usbManager?.deviceList ?: return false
            
            for (device in deviceList.values) {
                Log.d(TAG, "Device found: VID=${device.vendorId}, PID=${device.productId}")
                
                if (device.vendorId == VENDOR_ID && device.productId == PRODUCT_ID) {
                    Log.d(TAG, "Grow R102A found!")
                    usbDevice = device
                    return true
                }
            }
            
            Log.w(TAG, "Grow R102A not found")
            return false
        } catch (e: Exception) {
            Log.e(TAG, "Error checking device: ${e.message}")
            return false
        }
    }
    
    fun connect(): Boolean {
        try {
            val manager = usbManager ?: return false
            val device = usbDevice ?: return false
            
            if (!manager.hasPermission(device)) {
                Log.e(TAG, "No USB permission")
                return false
            }
            
            otgKey = OTG_KEY(manager, device)
            val ret = otgKey?.UsbOpen() ?: -1
            
            if (ret != DEVICE_SUCCESS) {
                Log.e(TAG, "Failed to open device. Error code: $ret")
                otgKey = null
                return false
            }
            
            Log.d(TAG, "Device opened successfully")
            
            val authRet = otgKey?.PSword() ?: -1
            
            if (authRet != PS_OK) {
                Log.e(TAG, "Authentication failed. Error code: $authRet")
                disconnect()
                return false
            }
            
            Log.d(TAG, "Device authenticated successfully")
            return true
            
        } catch (e: Exception) {
            Log.e(TAG, "Connection error: ${e.message}")
            e.printStackTrace()
            return false
        }
    }
    
    fun captureFingerprint(): ByteArray? {
        try {
            val key = otgKey ?: run {
                Log.e(TAG, "OTG_KEY not initialized")
                return null
            }
            
            Log.d(TAG, "Waiting for finger...")
            
            var timeout = 0
            while (key.PSGetImage(DEV_ADDR) != PS_NO_FINGER) {
                Thread.sleep(20)
                timeout++
                if (timeout > 50) break
            }
            
            timeout = 0
            while (key.PSGetImage(DEV_ADDR) == PS_NO_FINGER) {
                Thread.sleep(50)
                timeout++
                
                if (timeout > 600) {
                    Log.e(TAG, "Timeout waiting for finger")
                    return null
                }
            }
            
            Log.d(TAG, "Finger detected! Capturing image...")
            
            val fingerBuffer = ByteArray(IMAGE_WIDTH * IMAGE_HEIGHT)
            val upRet = key.PSUpImage(DEV_ADDR, fingerBuffer)
            
            if (upRet != PS_OK) {
                Log.e(TAG, "Failed to upload image. Error code: $upRet")
                return null
            }
            
            Log.d(TAG, "Image captured successfully: ${fingerBuffer.size} bytes")
            
            return convertToPng(fingerBuffer)
            
        } catch (e: Exception) {
            Log.e(TAG, "Capture error: ${e.message}")
            e.printStackTrace()
            return null
        }
    }
    
    private fun convertToPng(rawData: ByteArray): ByteArray? {
        try {
            val bitmap = Bitmap.createBitmap(IMAGE_WIDTH, IMAGE_HEIGHT, Bitmap.Config.ARGB_8888)
            
            for (y in 0 until IMAGE_HEIGHT) {
                for (x in 0 until IMAGE_WIDTH) {
                    val index = y * IMAGE_WIDTH + x
                    val gray = rawData[index].toInt() and 0xFF
                    val pixel = Color.rgb(gray, gray, gray)
                    bitmap.setPixel(x, y, pixel)
                }
            }
            
            val outputStream = ByteArrayOutputStream()
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
            val pngData = outputStream.toByteArray()
            
            Log.d(TAG, "Converted to PNG: ${pngData.size} bytes")
            
            return pngData
            
        } catch (e: Exception) {
            Log.e(TAG, "PNG conversion error: ${e.message}")
            e.printStackTrace()
            return null
        }
    }
    
    fun disconnect() {
        try {
            otgKey?.CloseCard(0)
            otgKey = null
            Log.d(TAG, "Device disconnected")
        } catch (e: Exception) {
            Log.e(TAG, "Disconnect error: ${e.message}")
        }
    }
}