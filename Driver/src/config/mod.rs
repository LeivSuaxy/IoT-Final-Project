use std::env;
use std::sync::OnceLock;

#[derive(Debug)]
pub struct AppConfig {
    pub handshake_key: String,
    pub secret_key: String,
    pub baud_rate: u32,
}

static CONFIG: OnceLock<AppConfig> = OnceLock::new();

pub fn load_config() {
    dotenv::dotenv().ok();

    let config = AppConfig {
        handshake_key: env::var("HANDSHAKE_KEY").unwrap_or_else(|_| "default_key".to_string()),
        secret_key: env::var("SECRET_KEY").unwrap_or_else(|_| "default_secret".to_string()),
        baud_rate: env::var("BAUD_RATE").unwrap_or_else(|_| 9600.to_string()).parse().unwrap(),
    };
    
    CONFIG.set(config).expect("Config already initialized");
}

pub fn get_config() -> &'static AppConfig {
    CONFIG.get().expect("Config not initialized")
}