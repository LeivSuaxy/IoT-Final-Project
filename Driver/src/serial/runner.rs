use std::error::Error;
use std::time::Duration;
use serialport::SerialPort;
use crate::serial::list_arduino_ports;

pub async fn initialize_serial_port() -> Result<Box<dyn SerialPort>, Box<dyn Error + Send + Sync>> {
    let arduino_ports = list_arduino_ports().await?;
    if arduino_ports.is_empty() {
        return Err("No se detectó ningún puerto Arduino".into());
    }

    let port_name = arduino_ports[0].port_name.clone();
    let baud_rate: u32 = 9600;
    let port = tokio::task::spawn_blocking(move || {
        serialport::new(port_name, baud_rate)
            .timeout(Duration::from_millis(100))
            .open()
    })
        .await??;

    println!("Abierto puerto {} a {} bps.", port.name().unwrap_or_default(), baud_rate);
    Ok(port)
}