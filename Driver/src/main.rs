mod serial;
mod server;
mod commands;
mod protocol;

use serial::{list_arduino_ports, process_serial_data_with_broadcast};
use server::tcp::run_tcp_server;
use commands::handler::handle_commands;
use serialport::{SerialPort, SerialPortInfo};
use std::error::Error;
use std::sync::{Arc, Mutex};
use std::time::Duration;
use tokio::sync::{broadcast, mpsc};

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error + Send + Sync>> {
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

async fn initialize_serial_port() -> Result<Box<dyn SerialPort>, Box<dyn Error + Send + Sync>> {
    let arduino_ports = list_arduino_ports().await?;
    if arduino_ports.is_empty() {
        return Err("No se detectó ningún puerto Arduino".into());
    }

    let port_name = arduino_ports[0].port_name.clone();
    let port = tokio::task::spawn_blocking(move || {
        serialport::new(port_name, 115200)
            .timeout(Duration::from_millis(100))
            .open()
    })
    .await??;

    println!("Abierto puerto {} a 9600 bps.", port.name().unwrap_or_default());
    Ok(port)
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
}