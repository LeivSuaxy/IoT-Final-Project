use crate::protocol::{MessageType, ProtocolMessage, SessionState};
use serialport::SerialPort;
use std::error::Error;
use std::sync::{Arc, Mutex};

pub async fn write_command_to_serial(
    mut message: ProtocolMessage,
    port_writer: Arc<Mutex<Box<dyn SerialPort>>>,
    session: Arc<Mutex<SessionState>>,
) -> Result<usize, Box<dyn Error + Send + Sync>> {
    if message.message_type != MessageType::AUTH {
        let is_handshake_message =
            message.data.starts_with("HDSHK_") || message.data.starts_with("HANDSHAKE_");

        if !is_handshake_message {
            let auth_hash = {
                let mut session_guard = session.lock().unwrap();
                session_guard.for_sending().calculate_next_hash(true)
            };

            message.auth = auth_hash;
        }
    }

    let command = message.to_string();
    println!("Sending: {}", command);

    let port_writer_clone = Arc::clone(&port_writer);
    let mut terminator = command;
    terminator.push('\n');

    tokio::task::spawn_blocking(move || {
        let mut port = port_writer_clone.lock().unwrap();
        let bytes_written = port.write(terminator.as_bytes())?;
        port.flush()?;
        Ok::<usize, Box<dyn Error + Send + Sync>>(bytes_written)
    })
    .await?
}
