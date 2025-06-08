mod commands;
mod config;
mod protocol;
mod security;
mod serial;
mod server;

use crate::protocol::SessionState;
use crate::security::HashBuilder;
use commands::handler::handle_commands;
use serial::{initialize_serial_port, process_serial_data_with_broadcast};
use serialport::SerialPort;
use server::tcp::run_tcp_server;
use std::error::Error;
use std::sync::{Arc, Mutex};
use std::time::Duration;
use tokio::sync::{broadcast, mpsc};

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error + Send + Sync>> {
    config::load_config();

    let (rfid_tx, _) = broadcast::channel::<String>(16);
    let (cmd_tx, cmd_rx) = mpsc::channel::<String>(16);

    let port = initialize_serial_port(config::get_config().baud_rate).await?;
    let port_writer = Arc::new(Mutex::new(port));
    
    start_tasks(port_writer, rfid_tx.clone(), cmd_rx).await;

    // Run socket for app comunications.
    run_tcp_server(rfid_tx, cmd_tx).await
}

/// Function to perform the initial tasks of the system.
/// Step.1: Perform the handshake with the arduino PCB.
/// Step.2: Spawn tasks for read serial port
/// Step.3: Spawn tasks for handle commands from Desktop System
async fn start_tasks(
    port_writer: Arc<Mutex<Box<dyn SerialPort>>>,
    rfid_tx: broadcast::Sender<String>,
    cmd_rx: mpsc::Receiver<String>,
) {
    let delay: u64 = 3; // Time delay to perform handshake, secure threads.
    
    println!("Waiting {} secs before start handshake...", delay);
    tokio::time::sleep(Duration::from_secs(delay)).await;
    
    // Handshake
    let session_state = match protocol::perform_handshake(port_writer.clone()).await {
        Ok(session) => {
            println!("Handshake completed successfully");
            Arc::new(Mutex::new(session))
        }
        Err(e) => {
            eprintln!("Handshake failed: {}", e);
            Arc::new(Mutex::new(SessionState::new(HashBuilder::new())))
        }
    };
    
    // Tarea para procesamiento RFID
    let port_rfid = Arc::clone(&port_writer);
    let session_rfid = Arc::clone(&session_state);
    tokio::spawn(async move {
        tokio::task::spawn_blocking(move || {
            if let Err(e) = process_serial_data_with_broadcast(port_rfid, rfid_tx, session_rfid) {
                eprintln!("Serial processing error: {}", e);
            }
        })
        .await
        .expect("Serial processing task failed");
    });

    // Tarea para comandos con session state
    let port_cmd = Arc::clone(&port_writer);
    let session_cmd = Arc::clone(&session_state);
    tokio::spawn(async move {
        handle_commands(cmd_rx, port_cmd, session_cmd)
            .await;
    });
}
