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
        Self {
            message_type,
            data: data.to_string(),
            auth: String::new(), // TODO Default empty auth, can be set later
        }
    }

    pub fn to_string(&self) -> String {
        format!("{}_{}", self.message_type, self.data)
    }

    pub fn from_string(message: &str) -> Option<Self> {
        let parts: Vec<&str> = message.splitn(2, '_').collect();
        if parts.len() != 2 {
            return None;
        }

        let message_type = match parts[0] {
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
            data: parts[1].to_string(),
            auth: String::new(), // TODO Default empty auth, can be set later
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

        let base_message: &str = parts[0];
        let expected_checksum: &str = parts[1];
        let actual_checksum: String = calculate_checksum(base_message);

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