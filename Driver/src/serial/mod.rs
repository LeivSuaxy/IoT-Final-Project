pub mod utils;
pub mod reader;
pub mod writer;

// Exportar funciones comunes
pub use reader::process_serial_data_with_broadcast;
pub use writer::write_command_to_serial;
pub use utils::list_arduino_ports;
pub use utils::process_ack_message;