// src/config/mod.rs
use std::env;
use std::sync::OnceLock;

#[derive(Debug)]
pub struct AppConfig {
    pub handshake_key: String,
    pub secret_key: String,
    // Otras configuraciones según necesites
}

static CONFIG: OnceLock<AppConfig> = OnceLock::new();

pub fn load_config() {
    // Asegúrate de cargar el archivo .env
    dotenv::dotenv().ok();

    let config = AppConfig {
        handshake_key: env::var("HANDSHAKE_KEY").unwrap_or_else(|_| "default_key".to_string()),
        secret_key: env::var("SECRET_KEY").unwrap_or_else(|_| "default_secret".to_string()),
        // Otros valores de configuración
    };

    // Inicializa la configuración global
    CONFIG.set(config).expect("Config already initialized");
}

pub fn get_config() -> &'static AppConfig {
    CONFIG.get().expect("Config not initialized")
}