use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::TcpStream,
    sync::{broadcast, mpsc},
};

pub async fn handle_client(
    socket: TcpStream,
    mut rfid_rx: broadcast::Receiver<String>,
    cmd_tx: mpsc::Sender<String>
) {
    let (reader, mut writer) = socket.into_split();
    let mut reader = BufReader::new(reader);
    let mut line = String::new();

    // Task for receiving RFID events and sending to client
    let rfid_task = tokio::spawn(async move {
        while let Ok(hash) = rfid_rx.recv().await {
            if let Err(e) = writer.write_all(format!("{}\n", hash).as_bytes()).await {
                eprintln!("Error writing to client: {}", e);
                break;
            }
        }
    });

    // Task for reading client commands
    let cmd_task = tokio::spawn(async move {
        loop {
            line.clear();
            match reader.read_line(&mut line).await {
                Ok(0) => {
                    break;
                },
                Ok(_) => {
                    let cmd = line.trim().to_string();
                    if !cmd.is_empty() {
                        println!("Received command: {}", cmd);
                        if let Err(e) = cmd_tx.send(cmd).await {
                            eprintln!("Error forwarding command: {}", e);
                            break;
                        }
                    }
                },
                Err(e) => {
                    eprintln!("Error reading from client: {}", e);
                    break;
                }
            }
        }
    });

    // Wait for either task to complete
    tokio::select! {
            _ = rfid_task => {},
            _ = cmd_task => {},
    }

    println!("Client disconnected");
}
