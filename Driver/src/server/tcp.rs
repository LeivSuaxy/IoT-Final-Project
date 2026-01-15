use std::error::Error;
use tokio::net::TcpListener;
use tokio::sync::{broadcast, mpsc};
use crate::server::client::handle_client;

const TCP_PORT: u16 = 8080;

pub async fn run_tcp_server(
    rfid_tx: broadcast::Sender<String>,
    cmd_tx: mpsc::Sender<String>
) -> Result<(), Box<dyn Error + Send + Sync>> {
    let listener = TcpListener::bind(format!("0.0.0.0:{}", TCP_PORT)).await?;
    println!("TCP server listening on port {}", TCP_PORT);

    loop {
        let (socket, addr) = listener.accept().await?;
        println!("New connection from {}", addr);

        let rfid_rx = rfid_tx.subscribe();
        let cmd_tx_clone = cmd_tx.clone();

        tokio::spawn(async move {
            handle_client(socket, rfid_rx, cmd_tx_clone).await;
        });
    }
}