package com.example.mysentinelapp

import android.annotation.SuppressLint
import android.bluetooth.*
import android.content.Context
import android.util.Log
import java.util.*

@SuppressLint("MissingPermission")
class BLEManager(private val context: Context) {
    private val bluetoothAdapter: BluetoothAdapter? by lazy {
        val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothManager.adapter
    }

    private var bluetoothGatt: BluetoothGatt? = null
    private var onDataReceived: ((String) -> Unit)? = null
    
    private var serviceUuid: UUID? = null
    private var characteristicUuid: UUID? = null
    private var aesKey: String? = null

    fun connectToDevice(
        deviceAddress: String, 
        serviceUuidString: String, 
        characteristicUuidString: String,
        aesKey: String,
        onDataReceived: (String) -> Unit
    ) {
        this.onDataReceived = onDataReceived
        this.serviceUuid = UUID.fromString(serviceUuidString)
        this.characteristicUuid = UUID.fromString(characteristicUuidString)
        this.aesKey = aesKey

        val device = bluetoothAdapter?.getRemoteDevice(deviceAddress)
        if (device == null) {
            Log.e("BLEManager", "Device not found: $deviceAddress")
            return
        }

        bluetoothGatt = device.connectGatt(context, false, gattCallback)
    }

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                Log.i("BLEManager", "Connected to GATT server.")
                gatt.discoverServices()
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.i("BLEManager", "Disconnected from GATT server.")
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val service = gatt.getService(serviceUuid)
                val characteristic = service?.getCharacteristic(characteristicUuid)
                
                if (characteristic != null) {
                    gatt.readCharacteristic(characteristic)
                } else {
                    Log.e("BLEManager", "Characteristic not found: $characteristicUuid")
                }
            }
        }

        @Deprecated("Deprecated in Java")
        override fun onCharacteristicRead(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic,
            status: Int
        ) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val data = characteristic.value?.let { bytes ->
                    // Here you would use the aesKey to decrypt if needed
                    // For now, we just return the raw string or hex
                    bytes.joinToString("") { "%02x".format(it) }
                } ?: ""
                onDataReceived?.invoke(data)
            }
        }
    }

    fun disconnect() {
        bluetoothGatt?.disconnect()
        bluetoothGatt?.close()
        bluetoothGatt = null
    }
}
