use serialport::{SerialPortInfo, available_ports};
use std::error::Error;
use tokio::task;

/// List all Serial ports connected to PC
/// Works for windows and linux systems
pub async fn list_arduino_ports() -> Result<Vec<SerialPortInfo>, Box<dyn Error + Send + Sync>> {
    let ports: Vec<SerialPortInfo> = task::spawn_blocking(|| available_ports())
        .await
        .map_err(|e| Box::new(e) as Box<dyn Error + Send + Sync>)?
        .map_err(|e| Box::new(e) as Box<dyn Error + Send + Sync>)?;

    #[cfg(target_os = "windows")]
    let filtered: Vec<SerialPortInfo> = ports
        .into_iter()
        .filter(|p| p.port_name.to_uppercase().starts_with("COM"))
        .collect();

    #[cfg(target_os = "linux")]
    let filtered: Vec<SerialPortInfo> = ports
        .into_iter()
        .filter(|p| {
            p.port_name.starts_with("/dev/ttyUSB") || p.port_name.starts_with("/dev/ttyACM")
        })
        .collect();

    Ok(filtered)
}
