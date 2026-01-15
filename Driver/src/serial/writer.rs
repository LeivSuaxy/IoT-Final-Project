use serialport::SerialPort;
use std::error::Error;
use std::sync::{Arc, Mutex};
use crate::protocol::ProtocolMessage;

pub async fn write_command_to_serial(
    command: String,
    port_writer: Arc<Mutex<Box<dyn SerialPort>>>
) -> Result<usize, Box<dyn Error + Send + Sync>> {
    let port_writer_clone = Arc::clone(&port_writer);
    let mut terminator = command.clone();
    terminator.push('\n');

    tokio::task::spawn_blocking(move || {
        let mut port = port_writer_clone.lock().unwrap();
        let bytes_written = port.write(terminator.as_bytes())?;
        port.flush()?;
        Ok::<usize, Box<dyn Error + Send + Sync>>(bytes_written)
    }).await?
}