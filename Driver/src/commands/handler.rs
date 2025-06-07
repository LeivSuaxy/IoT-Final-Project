use crate::protocol::{ProtocolMessage, SessionState};
use crate::serial::writer::write_command_to_serial;
use serialport::SerialPort;
use std::sync::{Arc, Mutex};
use tokio::sync::mpsc;

pub async fn handle_commands(
    mut cmd_rx: mpsc::Receiver<String>,
    port_writer: Arc<Mutex<Box<dyn SerialPort>>>,
    session: Arc<Mutex<SessionState>>,
) {
    while let Some(mut cmd) = cmd_rx.recv().await {
        // BOM delete
        if cmd.starts_with('\u{feff}'){
            cmd = cmd.trim_start_matches('\u{feff}').to_string();
        }
        
        if let Some(message) = ProtocolMessage::from_string(&cmd) {
            if let Err(e) = write_command_to_serial(message, port_writer.clone(), session.clone()).await {
                eprintln!("Error writing command: {}", e);
            }
        } else {
            eprintln!("Invalid command format received: {}", cmd);
        }
    }
}