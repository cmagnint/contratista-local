package com.terrasoft.contratista

import android.content.Context
import android.hardware.usb.*
import android.util.Log

class UsbFingerprintReader(private val context: Context) {
    
    private val TAG = "UsbFingerprintReader"
    private var usbDevice: UsbDevice? = null
    private var usbConnection: UsbDeviceConnection? = null
    private var usbInterface: UsbInterface? = null
    
    companion object {
        const val VENDOR_ID = 1466  // 0x05ba
        const val PRODUCT_ID = 10   // 0x000a
    }
    
    fun checkDevice(): Boolean {
        val manager = context.getSystemService(Context.USB_SERVICE) as UsbManager
        val deviceList = manager.deviceList
        
        for (device in deviceList.values) {
            Log.d(TAG, "Device: VID=${device.vendorId}, PID=${device.productId}")
            if (device.vendorId == VENDOR_ID && device.productId == PRODUCT_ID) {
                usbDevice = device
                return true
            }
        }
        return false
    }
    
    fun connect(): Boolean {
        val manager = context.getSystemService(Context.USB_SERVICE) as UsbManager
        usbDevice?.let { device ->
            if (!manager.hasPermission(device)) {
                Log.e(TAG, "No permission")
                return false
            }
            
            usbConnection = manager.openDevice(device)
            if (usbConnection == null) {
                Log.e(TAG, "Failed to open")
                return false
            }
            
            usbInterface = device.getInterface(0)
            usbConnection?.claimInterface(usbInterface, true)
            
            Log.d(TAG, "Connected")
            return true
        }
        return false
    }
    
    fun captureFingerprint(): ByteArray? {
        try {
            val captureCommand = byteArrayOf(0x01, 0x00, 0x00, 0x00)
            
            val endpoint = usbInterface?.getEndpoint(0)
            endpoint?.let {
                val sent = usbConnection?.bulkTransfer(it, captureCommand, captureCommand.size, 5000)
                Log.d(TAG, "Sent: $sent")
                
                val buffer = ByteArray(307200)
                val received = usbConnection?.bulkTransfer(it, buffer, buffer.size, 10000)
                
                Log.d(TAG, "Received: $received")
                
                if (received != null && received > 0) {
                    return buffer.copyOf(received)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error: ${e.message}")
        }
        return null
    }
    
    fun disconnect() {
        usbInterface?.let {
            usbConnection?.releaseInterface(it)
        }
        usbConnection?.close()
    }
}