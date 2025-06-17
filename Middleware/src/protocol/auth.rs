use crate::config;
use crate::protocol::{MessageType, ProtocolMessage};
use crate::security::HashBuilder;
use hmac::{Hmac, Mac};
use lazy_static::lazy_static;
use serialport::SerialPort;
use sha2::Sha256;
use std::error::Error;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};

lazy_static! {
    static ref SESSION: Mutex<Option<SessionState>> = Mutex::new(None);
    static ref HANDSHAKE_IN_PROGRESS: AtomicBool = AtomicBool::new(false);
}

pub fn initialize_session(hash_builder: HashBuilder) {
    let mut session = SESSION.lock().unwrap();
    *session = Some(SessionState::new(hash_builder));
}

pub fn get_auth_for_message() -> String {
    let mut session = SESSION.lock().unwrap();
    if let Some(state) = session.as_mut() {
        if state.needs_rehandshake() {
            // Signal that a handshake is needed
            HANDSHAKE_IN_PROGRESS.store(true, Ordering::SeqCst);
            return "REHANDSHAKE".to_string();
        }
        state.for_sending().calculate_next_hash(true)
    } else {
        // No session, cannot authenticate
        "".to_string()
    }
}

pub fn validate_received_message(auth: &str) -> bool {
    let mut session = SESSION.lock().unwrap();
    if let Some(state) = session.as_mut() {
        if auth == "REHANDSHAKE" {
            HANDSHAKE_IN_PROGRESS.store(true, Ordering::SeqCst);
            return true; // Accept rehandshake request
        }
        state.for_receiving().validate_hash(auth)
    } else {
        false
    }
}

pub async fn perform_handshake(
    port: Arc<Mutex<Box<dyn SerialPort>>>,
) -> Result<SessionState, Box<dyn Error>> {
    let hash_builder = HashBuilder::new();

    // Generate client nonce
    let client_nonce = generate_nonce(&hash_builder, Some(true));

    // Send handshake initiation
    send_handshake_request(Arc::clone(&port), &hash_builder, &client_nonce)
        .await
        .expect("Cannot perform the handshake");

    Ok(SessionState::new(hash_builder))
}

fn generate_hash(key: &str, init: u32, step: u32, limit: u32) -> String {
    let f_part1 = init * step;
    let f_part2 = limit + step;
    let f_part3 = step + limit - init;

    format!("{}{}{}{}", key, f_part1, f_part2, f_part3)
}

fn hash_key(key: &str) -> String {
    use sha2::{Digest, Sha256};
    let mut hasher = Sha256::new();
    hasher.update(key.as_bytes());
    let result = hasher.finalize();

    // Trunk string on 16 chars
    hex::encode(&result[0..16])
}

fn generate_nonce(hash_builder: &HashBuilder, handshake: Option<bool>) -> String {
    let handshake = handshake.unwrap_or(false);
    let secret_key: &str;

    if !handshake {
        secret_key = &config::get_config().secret_key;
    } else {
        secret_key = &config::get_config().handshake_key;
    }

    let combined = generate_hash(
        secret_key,
        hash_builder.init,
        hash_builder.step,
        hash_builder.limit,
    );

    hash_key(&combined)
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

    tokio::task::spawn_blocking(move || {
        let mut port_guard = port.lock().unwrap();
        port_guard.write(format!("{}\n", command.to_string()).as_bytes())
    })
    .await??;
    Ok(())
}

/*async fn receive_handshake_response(
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
}*/

// SessionState
#[derive(Debug)]
pub struct SessionState {
    init: u32,
    step: u32,
    limit: u32,
    is_sending: bool,
}

impl SessionState {
    pub fn new(hash_builder: HashBuilder) -> Self {
        Self {
            init: hash_builder.init,
            step: hash_builder.step,
            limit: hash_builder.limit,
            is_sending: false,
        }
    }

    pub fn for_sending(&mut self) -> &mut Self {
        self.is_sending = true;
        self
    }

    pub fn for_receiving(&mut self) -> &mut Self {
        self.is_sending = false;
        self
    }

    pub fn calculate_next_hash(&mut self, increment: bool) -> String {
        let secret_key = &config::get_config().secret_key;
        let combined = generate_hash(secret_key, self.init, self.step, self.limit);
        
        if increment {
            self.init += self.step;
        }

        hash_key(&combined)
    }

    pub fn needs_rehandshake(&self) -> bool {
        self.init > self.limit
    }
    
    pub fn validate_hash(&mut self, received_hash: &str) -> bool {
        let expected_hash = self.calculate_next_hash(true);
        expected_hash == received_hash
    }
}
