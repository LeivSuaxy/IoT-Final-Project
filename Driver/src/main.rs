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

    // Configurar canales
    let (rfid_tx, _) = broadcast::channel::<String>(16);
    let (cmd_tx, cmd_rx) = mpsc::channel::<String>(16);

    // Inicializar puerto serial
    let port = initialize_serial_port().await?;
    let port_writer = Arc::new(Mutex::new(port));

    // Iniciar tareas
    start_tasks(port_writer, rfid_tx.clone(), cmd_rx).await;

    // Ejecutar servidor TCP
    run_tcp_server(rfid_tx, cmd_tx).await
}

async fn start_tasks(
    port_writer: Arc<Mutex<Box<dyn SerialPort>>>,
    rfid_tx: broadcast::Sender<String>,
    cmd_rx: mpsc::Receiver<String>,
) {
    println!("Esperando 10 segundos antes de iniciar el handshake...");
    tokio::time::sleep(Duration::from_secs(3)).await;
    // Perform handshake and get session state
    let session_state = match protocol::perform_handshake(port_writer.clone()).await {
        Ok(session) => {
            println!("Handshake completed successfully");
            Arc::new(Mutex::new(session))
        }
        Err(e) => {
            eprintln!("Handshake failed: {}", e);
            // If handshake fails, create a default session state
            Arc::new(Mutex::new(SessionState::new(HashBuilder::new())))
        }
    };
    println!("Session state: {:?}", session_state);

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
        handle_commands(cmd_rx, port_cmd, session_cmd).await;
    });
}
