package com.example.mysentinelapp

import kotlinx.serialization.Serializable

@Serializable
data class QRData(
    val m: String, // MAC Address
    val s: String, // Service UUID
    val c: String, // Characteristic UUID
    val k: String  // AES Key
)
