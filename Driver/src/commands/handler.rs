use serialport::SerialPort;
use std::error::Error;
use std::sync::{Arc, Mutex};
use tokio::sync::mpsc;
use crate::serial::writer::write_command_to_serial;

pub async fn handle_commands(
    mut cmd_rx: mpsc::Receiver<String>,
    port_writer: Arc<Mutex<Box<dyn SerialPort>>>,
) {
    println!("Command handler started and waiting for commands");

    while let Some(cmd) = cmd_rx.recv().await {
        println!("Sending to Arduino: {:?}", cmd);
        
        match write_command_to_serial(cmd, Arc::clone(&port_writer)).await {
            Ok(bytes_written) => println!("Successfully wrote {} bytes to serial port", bytes_written),
            Err(e) => eprintln!("Error writing to serial port: {}", e),
        }
    }
}