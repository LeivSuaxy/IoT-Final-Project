mod serial;
mod server;
mod commands;
mod protocol;
mod config;
mod security;

use serial::{list_arduino_ports, process_serial_data_with_broadcast, initialize_serial_port};
use server::tcp::run_tcp_server;
use commands::handler::handle_commands;
use serialport::{SerialPort, SerialPortInfo};
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
    // Tarea para procesamiento RFID
    let port_rfid = Arc::clone(&port_writer);
    tokio::spawn(async move {
        tokio::task::spawn_blocking(move || {
            if let Err(e) = process_serial_data_with_broadcast(port_rfid, rfid_tx) {
                eprintln!("Serial processing error: {}", e);
            }
        })
        .await
        .expect("Serial processing task failed");
    });

    // Tarea para comandos
    let port_cmd = Arc::clone(&port_writer);
    tokio::spawn(async move {
        handle_commands(cmd_rx, port_cmd).await;
    });

    // Esperar 10 segundos antes de iniciar el handshake
        println!("Esperando 10 segundos antes de iniciar el handshake...");
        tokio::time::sleep(Duration::from_secs(3)).await;
        
        match protocol::perform_handshake(port_writer.clone()).await {
            Ok(_) => println!("Handshake completed successfully"),
            Err(e) => {
                eprintln!("Handshake failed: {}", e);
                //return Err(e);
            }
        }
}