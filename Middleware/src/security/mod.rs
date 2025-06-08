use rand::Rng;
#[derive(Debug)]
pub struct HashBuilder {
    pub init: u32,
    pub step: u32,
    pub limit: u32,
}

impl HashBuilder {
    pub fn new() -> Self {
        let mut rng = rand::thread_rng();
        Self {
            init: rng.gen_range(1..=1000),
            step: rng.gen_range(1..=25),
            limit: rng.gen_range(4000..=9000),
        }
    }
    
    pub fn to_string(&self) -> String {
        format!("{}:{}:{}", self.init, self.step, self.limit)
    }
}