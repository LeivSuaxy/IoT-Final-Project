// src/handshake.rs
use std::error::Error;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use rand::Rng;
use hmac::{Hmac, Mac};
use sha2::Sha256;
use serialport::SerialPort;
use crate::config;
use crate::protocol::{MessageType, ProtocolMessage};
use crate::security::HashBuilder;

type HmacSha256 = Hmac<Sha256>;

pub async fn perform_handshake(
    port: Arc<Mutex<Box<dyn SerialPort>>>,
) -> Result<(), Box<dyn Error + Send + Sync>> {
    println!("Starting handshake with Arduino...");
    
    let hash_builder = HashBuilder::new();
    
    // Generate client nonce
    let client_nonce = generate_nonce(&hash_builder);

    // Send handshake initiation
    send_handshake_request(Arc::clone(&port), &hash_builder, &client_nonce).await?;

    // Receive server response with nonce and HMAC
    let (server_nonce, server_hmac) = receive_handshake_response(Arc::clone(&port)).await?;

    // Verify server HMAC
    /*verify_server_hmac(&client_nonce, &server_nonce, &server_hmac)?;

    // Generate and send client HMAC
    send_client_hmac(Arc::clone(&port), &client_nonce, &server_nonce).await?;

    // Wait for final ACK
    receive_handshake_ack(Arc::clone(&port)).await?;

    println!("Handshake completed successfully, sequence initialized to 0");*/
    Ok(())
}

fn generate_nonce(hash_builder: &HashBuilder) -> String {
    let secret_key = config::get_config().handshake_key.clone();
    println!("{}", secret_key);
    let formula_part1 = hash_builder.init * hash_builder.step;
    let formula_part2 = hash_builder.limit + hash_builder.step;
    let formula_part3 = hash_builder.step + hash_builder.limit - hash_builder.init;
    println!("{:?}", hash_builder);
    let combined = format!("{}{}{}{}", secret_key, formula_part1, formula_part2, formula_part3);
    println!("{}", combined);
    
    use sha2::{Sha256, Digest};
    let mut hasher = Sha256::new();
    hasher.update(combined.as_bytes());
    let result = hasher.finalize();
    
    // Truncar a 16 bytes (128 bits) - suficiente para la mayoría de aplicaciones
    hex::encode(&result[0..16])
}

async fn send_handshake_request(
    port: Arc<Mutex<Box<dyn SerialPort>>>,
    hash_builder: &HashBuilder,
    nonce: &str,
) -> Result<(), Box<dyn Error + Send + Sync>> {
    let command = ProtocolMessage::new(
        MessageType::AUTH,
        &format!("HDSHK_INIT|{}&{}", nonce, &hash_builder.to_string()) as &str,
    );
    
    println!("{}", command.to_string());
    println!("{}", command.data);

    tokio::task::spawn_blocking(move || {
        let mut port_guard = port.lock().unwrap();
        port_guard.write(format!("{}\n", command.to_string()).as_bytes())
    }).await??;
    // 7e6cbdb324ad9a24bc6ecd304378c8fd
    // e3b0c44298fc1c149afbf4c8996fb924
    Ok(())
}

async fn receive_handshake_response(
    port: Arc<Mutex<Box<dyn SerialPort>>>,
) -> Result<(String, String), Box<dyn Error + Send + Sync>> {
    let timeout = Duration::from_secs(5);
    let start = Instant::now();
    let mut buffer = String::new();

    while start.elapsed() < timeout {
        let mut read_buf = [0u8; 64];
        
        let port_clone = Arc::clone(&port);
        let bytes_read = tokio::task::spawn_blocking(move || {
            let mut port_guard = port_clone.lock().unwrap();
            port_guard.read(&mut read_buf)
        }).await??;

        if bytes_read > 0 {
            if let Ok(s) = String::from_utf8(read_buf[..bytes_read].to_vec()) {
                buffer.push_str(&s);

                if let Some(pos) = buffer.find('\n') {
                    let response = buffer[..pos].trim();

                    // Parse HANDSHAKE_RESP:nonce:hmac
                    if response.starts_with("HANDSHAKE_RESP:") {
                        let parts: Vec<&str> = response.splitn(3, ':').collect();
                        if parts.len() == 3 {
                            return Ok((parts[1].to_string(), parts[2].to_string()));
                        }
                    }
                }
            }
        }

        tokio::time::sleep(Duration::from_millis(50)).await;
    }

    Err("Handshake response timeout".into())
}

fn verify_server_hmac(
    client_nonce: &str,
    server_nonce: &str,
    server_hmac: &str,
) -> Result<(), Box<dyn Error + Send + Sync>> {
    let secret_key = config::get_config().secret_key.as_bytes();

    let mut mac = HmacSha256::new_from_slice(secret_key)?;
    mac.update(server_nonce.as_bytes());
    mac.update(client_nonce.as_bytes());

    let hmac_bytes = mac.finalize().into_bytes();
    let expected_hmac = hex::encode(hmac_bytes);

    if expected_hmac == server_hmac {
        Ok(())
    } else {
        Err("Server HMAC verification failed".into())
    }
}

async fn send_client_hmac(
    port: Arc<Mutex<Box<dyn SerialPort>>>,
    client_nonce: &str,
    server_nonce: &str,
) -> Result<(), Box<dyn Error + Send + Sync>> {
    let secret_key = config::get_config().secret_key.as_bytes();

    let mut mac = HmacSha256::new_from_slice(secret_key)?;
    mac.update(client_nonce.as_bytes());
    mac.update(server_nonce.as_bytes());

    let hmac_bytes = mac.finalize().into_bytes();
    let client_hmac = hex::encode(hmac_bytes);

    let command = format!("HANDSHAKE_AUTH:{}", client_hmac);
    
    let port_clone = Arc::clone(&port);
    tokio::task::spawn_blocking(move || {
        let mut port_guard = port_clone.lock().unwrap();
        port_guard.write_all(format!("{}\n", command).as_bytes())
    }).await??;

    Ok(())
}

async fn receive_handshake_ack(
    port: Arc<Mutex<Box<dyn SerialPort>>>,
) -> Result<(), Box<dyn Error + Send + Sync>> {
    let timeout = Duration::from_secs(5);
    let start = Instant::now();
    let mut buffer = String::new();

    while start.elapsed() < timeout {
        let mut read_buf = [0u8; 64];

        let port_clone = Arc::clone(&port);
        let bytes_read = tokio::task::spawn_blocking(move || {
            let mut port_guard = port_clone.lock().unwrap();
            port_guard.read(&mut read_buf)
        }).await??;

        if bytes_read > 0 {
            if let Ok(s) = String::from_utf8(read_buf[..bytes_read].to_vec()) {
                buffer.push_str(&s);

                if let Some(pos) = buffer.find('\n') {
                    let response = buffer[..pos].trim();

                    if response == "HANDSHAKE_ACK" {
                        return Ok(());
                    }
                }
            }
        }

        tokio::time::sleep(Duration::from_millis(50)).await;
    }

    Err("Handshake acknowledgment timeout".into())
}