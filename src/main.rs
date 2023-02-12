use chrono::{DateTime, Utc};
use core::fmt;
use hex;
use p256::ecdsa::{signature::Signer, signature::Verifier, Signature, SigningKey, VerifyingKey};
use rand_core::OsRng;
use sha2::{Digest, Sha256};

#[derive(Copy, Clone)]
struct Location {
    longitude: f64,
    latitude: f64,
}

impl fmt::Display for Location {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.longitude, self.latitude)
    }
}

struct Block {
    device_id: u32,
    from: Location,
    to: Location,
    timestamp: DateTime<Utc>,
    previous_hash: String,
    hash: String,
}

fn create_new_block(device_id: u32, from: Location, to: Location, previous_hash: String) -> Block {
    let mut b: Block = Block {
        device_id: device_id,
        from: from,
        to: to,
        timestamp: Utc::now(),
        previous_hash: previous_hash,
        hash: String::new(),
    };
    b.hash = b.compute_hash();
    return b;
}

impl Block {
    fn compute_hash(&self) -> String {
        let mut hasher = Sha256::new();

        hasher.update(self.device_id.to_string());
        hasher.update(self.from.to_string());
        hasher.update(self.to.to_string());
        hasher.update(self.timestamp.to_string());
        hasher.update(self.previous_hash.clone());

        return hex::encode(hasher.finalize().to_vec());
    }
}

struct Chain {
    chain: Vec<Block>,
}

fn create_new_chain() -> Chain {
    return Chain { chain: Vec::new() };
}

impl Chain {
    fn try_add_block(&mut self, b: Block) -> bool {
        if self.chain.is_empty() {
            self.chain.push(b);
            return true;
        }

        // check that the new block's hash is correct
        if b.hash != b.compute_hash() {
            return false;
        }
        // check that the new block's previous hash is correct
        let r: bool = match self.chain.last() {
            None => false,
            Some(block) => block.hash == b.previous_hash,
        };
        if !r {
            return false;
        }

        // if no checks fail, then append the new block
        self.chain.push(b);
        return true;
    }
}

struct KeyLibrary {
    keys: Vec<VerifyingKey>,
}

fn main() {
    let l: Location = Location {
        longitude: 5.7,
        latitude: 6.2,
    };

    let b1: Block = create_new_block(0, l, l, String::from("genesis"));
    let b2: Block = create_new_block(1, l, l, b1.hash.clone());

    let mut c: Chain = create_new_chain();

    c.try_add_block(b1);
    c.try_add_block(b2);

    // println!("{}", c.chain[0].hash);
    // println!("{}", c.chain[1].hash);

    let signing_key: SigningKey = SigningKey::random(&mut OsRng); // Serialize with `::to_bytes()`
    let sk = signing_key.to_bytes();
    let sk_string: String = hex::encode(sk);
    println!("{}", sk_string);
    let message = b"ECDSA proves knowledge of a secret number in the context of a single message";
    let signature: Signature = signing_key.sign(message);
    println!("{}", signature);
}
