use std::error::Error;
use std::sync::{Arc, Mutex};
use std::time::Duration;
use serialport::SerialPort;
use tokio::sync::broadcast;
use crate::protocol::{MessageType, ProtocolMessage};
use crate::serial::utils::process_ack_message;

pub fn process_serial_data_with_broadcast(
    port: Arc<Mutex<Box<dyn SerialPort>>>,
    tx: broadcast::Sender<String>,
) -> Result<(), Box<dyn Error + Send + Sync>> {
    let mut buffer = String::with_capacity(128);
    let mut read_buf = [0u8; 64];

    println!("Starting RFID hash monitoring...");

    loop {
        let mut port_guard = port.lock().unwrap();
        match port_guard.read(&mut read_buf) {
            Ok(n) if n > 0 => {
                if let Ok(s) = String::from_utf8(read_buf[..n].to_vec()) {
                    buffer.push_str(&s);

                    while let Some(pos) = buffer.find('\n') {
                        let line = buffer[..pos].trim();
                        
                        if let Some(message) = ProtocolMessage::from_string(line) {
                            println!("Received message: {:?}", message);
                            
                            let _ = tx.send(message.clone().to_string());
                            
                            if message.message_type == MessageType::AUTH {
                                println!("Received AUTH message: {:?}", message);
                            }
                            
                            
                        } else {
                            eprintln!("Received invalid protocol message: {}", line);
                            let _ = tx.send(ProtocolMessage::new(
                                MessageType::ERR,
                                "Invalid protocol message",
                            ).to_string());
                        }
                        buffer.drain(..=pos);
                    }
                }
            }
            Ok(_) => {
                drop(port_guard); // Release lock while sleeping
                std::thread::sleep(Duration::from_millis(10));
            }
            Err(e) if e.kind() == std::io::ErrorKind::TimedOut => {
                drop(port_guard); // Release lock while sleeping
                std::thread::sleep(Duration::from_millis(10));
            }
            Err(e) => {
                eprintln!("Warning: Error reading from serial port: {}", e);
                drop(port_guard); // Release lock while sleeping
                std::thread::sleep(Duration::from_millis(100));
            }
        }
    }
}