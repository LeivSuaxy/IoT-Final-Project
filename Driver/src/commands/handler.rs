use crate::protocol::{ProtocolMessage, SessionState};
use crate::serial::writer::write_command_to_serial;
use serialport::SerialPort;
use std::sync::{Arc, Mutex};
use tokio::sync::mpsc;

// En commands/handler.rs
pub async fn handle_commands(
    mut cmd_rx: mpsc::Receiver<String>,
    port_writer: Arc<Mutex<Box<dyn SerialPort>>>,
    session: Arc<Mutex<SessionState>>,
) {
    while let Some(mut cmd) = cmd_rx.recv().await {
        // Primero validar si el mensaje tiene formato correcto
        if cmd.starts_with('\u{feff}'){
            // Eliminar BOM si está presente
            cmd = cmd.trim_start_matches('\u{feff}').to_string();
        }
        
        if let Some(message) = ProtocolMessage::from_string(&cmd) {
            // Solo mensajes válidos pasan a write_command_to_serial
            if let Err(e) = write_command_to_serial(message, port_writer.clone(), session.clone()).await {
                eprintln!("Error writing command: {}", e);
            }
        } else {
            // Para mensajes inválidos, solo enviamos error pero NO usamos write_command_to_serial
            // que modificaría el estado de la sesión
            eprintln!("Invalid command format received: {}", cmd);

            // Opcional: enviar respuesta de error al cliente sin usar el estado de sesión
            // Esto requeriría un canal adicional para respuestas
        }
    }
}