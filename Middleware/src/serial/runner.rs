use crate::serial::list_arduino_ports;
use serialport::{SerialPort, SerialPortInfo};
use std::error::Error;
use std::time::Duration;

/// Initialize serial port with the first serial port connected with PC.
pub async fn initialize_serial_port(
    baud_rate: u32,
) -> Result<Box<dyn SerialPort>, Box<dyn Error + Send + Sync>> {
    let arduino_ports: Vec<SerialPortInfo> = list_arduino_ports().await?;
    if arduino_ports.is_empty() {
        return Err("Doesn't detect any Firmware port".into());
    }

    let port_name: String = arduino_ports[0].port_name.clone();
    let port = tokio::task::spawn_blocking(move || {
        serialport::new(port_name, baud_rate)
            .timeout(Duration::from_millis(100))
            .open()
    })
    .await??;

    println!(
        "Open port {} at {} bps.",
        port.name().unwrap_or_default(),
        baud_rate
    );
    Ok(port)
}
