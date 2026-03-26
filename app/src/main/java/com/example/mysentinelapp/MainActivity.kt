package com.example.mysentinelapp

import android.Manifest
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.example.mysentinelapp.ui.theme.MySentinelAppTheme
import kotlinx.serialization.json.Json

class MainActivity : ComponentActivity() {
    private lateinit var bleManager: BLEManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        bleManager = BLEManager(this)
        enableEdgeToEdge()
        setContent {
            MySentinelAppTheme {
                MainScreen(bleManager)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        bleManager.disconnect()
    }
}

@Composable
fun MainScreen(bleManager: BLEManager) {
    val context = LocalContext.current
    var qrData by remember { mutableStateOf<QRData?>(null) }
    val bleData = remember { mutableStateListOf<String>() }
    var isScanning by remember { mutableStateOf(true) }

    val permissionsToRequest = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.BLUETOOTH_SCAN,
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
    } else {
        arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.entries.all { it.value }
        if (!allGranted) {
            Toast.makeText(context, "Permissions required for scanner and BLE", Toast.LENGTH_SHORT).show()
        }
    }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(permissionsToRequest)
    }

    Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            if (isScanning) {
                Text(
                    text = "Scan Device QR Code",
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.padding(16.dp)
                )
                QRScannerView(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                    onQrCodeScanned = { jsonString ->
                        if (isScanning) {
                            try {
                                val data = Json.decodeFromString<QRData>(jsonString)
                                qrData = data
                                isScanning = false
                                Toast.makeText(context, "Device Found: ${data.m}", Toast.LENGTH_SHORT).show()
                                
                                bleManager.connectToDevice(
                                    deviceAddress = data.m,
                                    serviceUuidString = data.s,
                                    characteristicUuidString = data.c,
                                    aesKey = data.k
                                ) { received ->
                                    bleData.add(received)
                                }
                            } catch (e: Exception) {
                                e.printStackTrace()
                                // Optionally show error but keep scanning
                                // Toast.makeText(context, "Invalid QR Format", Toast.LENGTH_SHORT).show()
                            }
                        }
                    }
                )
            } else {
                Text(
                    text = "Connected to: ${qrData?.m}",
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.padding(16.dp)
                )
                qrData?.let {
                    Text("Service: ${it.s}", style = MaterialTheme.typography.bodySmall)
                    Text("Characteristic: ${it.c}", style = MaterialTheme.typography.bodySmall)
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Button(onClick = { 
                    bleManager.disconnect()
                    isScanning = true 
                    bleData.clear()
                    qrData = null
                }) {
                    Text("Disconnect & Scan Again")
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                Text(text = "Received Data (Hex):", style = MaterialTheme.typography.titleMedium)
                LazyColumn(modifier = Modifier.weight(1f)) {
                    items(bleData) { item ->
                        Text(text = item, modifier = Modifier.padding(8.dp))
                        HorizontalDivider()
                    }
                }
            }
        }
    }
}
