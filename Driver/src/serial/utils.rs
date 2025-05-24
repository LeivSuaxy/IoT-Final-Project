use std::error::Error;
use serialport::{available_ports, SerialPortInfo, SerialPort};
use tokio::task;
use std::time::{Duration, Instant};
use tokio::sync::broadcast;


pub async fn list_arduino_ports() -> Result<Vec<SerialPortInfo>, Box<dyn Error + Send + Sync>> {
    let ports: Vec<SerialPortInfo> = task::spawn_blocking(|| available_ports()).await
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
            p.port_name.starts_with("/dev/ttyUSB")
                || p.port_name.starts_with("/dev/ttyACM")
        })
        .collect();

    Ok(filtered)
}

pub fn process_serial_data(mut port: Box<dyn SerialPort>) -> Result<(), Box<dyn Error + Send + Sync>> {
    let mut buffer = String::with_capacity(128);
    let mut read_buf = [0u8; 64];
    let mut last_activity = Instant::now();

    println!("Starting RFID hash monitoring...");

    loop {
        match port.read(&mut read_buf) {
            Ok(n) if n > 0 => {
                // Reset timeout when we get data
                last_activity = Instant::now();

                // Convert bytes to string and append to buffer
                if let Ok(s) = String::from_utf8(read_buf[..n].to_vec()) {
                    buffer.push_str(&s);

                    // Process complete lines
                    while let Some(pos) = buffer.find('\n') {
                        let line = buffer[..pos].trim();

                        // Validate hash (64 hex characters)
                        if line.len() == 64 && line.chars().all(|c| c.is_ascii_hexdigit()) {
                            println!("Complete hash received: {}", line);
                            // Process the hash here
                        } else {
                            println!("Received data (not a complete hash): {}", line);
                        }

                        // Remove processed line from buffer
                        buffer.drain(..=pos);
                    }
                }
            },
            Ok(_) => {
                // No data - normal condition, just wait
                std::thread::sleep(Duration::from_millis(10));
            },
            Err(e) if e.kind() == std::io::ErrorKind::TimedOut => {
                // Timeout is normal - just continue
                std::thread::sleep(Duration::from_millis(10));
            },
            Err(e) => {
                // Log actual errors but don't exit
                eprintln!("Warning: Error reading from serial port: {}", e);
                std::thread::sleep(Duration::from_millis(100));
                // Only exit on persistent errors
                if last_activity.elapsed() > Duration::from_secs(300) {  // 5 minutes
                    return Err(e.into());
                }
            }
        }
    }
}

pub fn process_ack_message(message: &str, tx: &broadcast::Sender<String>) {
    // Split the message to get type and data
    let parts: Vec<&str> = message.split('_').collect();

    if parts.len() < 2 {
        println!("Invalid ACK format: {}", message);
        return;
    }

    let ack_type = parts[1];

    match ack_type {
        "CMD" => {
            // ACK_CMD_success/failure message
            if parts.len() >= 3 {
                let status = parts[2];
                println!("Command acknowledgment: {}", status);
                // Broadcast the ACK to connected clients
                let _ = tx.send(message.to_string());
            }
        }
        "STATUS" => {
            // ACK_STATUS_details
            if parts.len() >= 3 {
                let status_info = parts[2];
                println!("Status update: {}", status_info);
                let _ = tx.send(message.to_string());
            }
        }
        // Add more ACK types as needed
        _ => {
            println!("Unknown ACK type: {}", ack_type);
            // Still broadcast unknown ACKs for logging/debugging
            let _ = tx.send(message.to_string());
        }
    }
}