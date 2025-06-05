use std::fmt;
use std::{format, write};

#[derive(Debug, Clone, PartialEq)]
pub enum MessageType{
    AUTH, // Authentication message to verify identity
    INFO, // Info message to transfer pure data
    ERR, // Error message to warn
    ACK, // Acknowledgment message to confirm
    MISS, // Missed message to warn about missing data
    CMD, // Command message to execute a specific action
    OK, // Ok message to confirm success of process
}

impl fmt::Display for MessageType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            MessageType::AUTH => write!(f, "AUTH"),
            MessageType::INFO => write!(f, "INFO"),
            MessageType::ERR => write!(f, "ERR"),
            MessageType::ACK => write!(f, "ACK"),
            MessageType::MISS => write!(f, "MISS"),
            MessageType::CMD => write!(f, "CMD"),
            MessageType::OK => write!(f, "OK"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct ProtocolMessage {
    pub message_type: MessageType,
    pub data: String,
    pub auth: String,
}

impl ProtocolMessage {
    pub fn new(message_type: MessageType, data: &str) -> Self {
        let auth = crate::protocol::auth::get_auth_for_message();
        Self {
            message_type,
            data: data.to_string(),
            auth, // TODO Default empty auth, can be set later
        }
    }

    pub fn with_auth(mut self, auth: &str) -> Self {
        self.auth = auth.to_string();
        self
    }

    pub fn to_string(&self) -> String {
        if self.auth.is_empty() {
            return format!("{}_{}", self.message_type, self.data);
        } else {
            return format!("{}_{}{}{}", self.message_type, self.data, "|", self.auth);
        }
    }

    pub fn from_string(message: &str) -> Option<Self> {
        // First split by pipe to separate message and auth
        let parts: Vec<&str> = message.splitn(2, '|').collect();
        let (base_message, auth) = if parts.len() == 2 {
            (parts[0], parts[1].to_string())
        } else {
            (message, String::new())
        };

        // Then parse the message type and data
        let msg_parts: Vec<&str> = base_message.splitn(2, '_').collect();
        if msg_parts.len() != 2 {
            return None;
        }

        let message_type = match msg_parts[0] {
            "AUTH" => MessageType::AUTH,
            "INFO" => MessageType::INFO,
            "ERR" => MessageType::ERR,
            "ACK" => MessageType::ACK,
            "MISS" => MessageType::MISS,
            "CMD" => MessageType::CMD,
            "OK" => MessageType::OK,
            _ => return None,
        };

        Some(Self {
            message_type,
            data: msg_parts[1].to_string(),
            auth,
        })
    }

    pub fn to_string_with_checksum(&self) -> String {
        let base_message = self.to_string();
        let checksum = calculate_checksum(&base_message);
        format!("{};{}", base_message, checksum)
    }

    pub fn from_string_with_checksum(message: &str) -> Option<Self> {
        let parts: Vec<&str> = message.splitn(2, ';').collect();
        if parts.len() != 2 {
            return None;
        }

        let base_message = parts[0];
        let expected_checksum = parts[1];
        let actual_checksum = calculate_checksum(base_message);

        if expected_checksum != actual_checksum {
            return None;
        }

        Self::from_string(base_message)
    }
}

fn calculate_checksum(message: &str) -> String {
    let mut sum: u16 = 0;
    for byte in message.bytes() {
        sum = sum.wrapping_add(byte as u16);
    }
    format!("{:04X}", sum)
}