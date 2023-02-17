use chrono::{DateTime, Utc};
use p256::EncodedPoint;
use core::fmt;
use std::io::Write;
use hex;
use p256::ecdsa::{signature::Signer, signature::Verifier, Signature, SigningKey, VerifyingKey};
use rand_core::OsRng;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::fs::File;
use std::io::{prelude::*, BufReader};

#[derive(Clone)]
struct Location {
    name: String,
    longitude: f64,
    latitude: f64,
}

impl fmt::Display for Location {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} ({}, {})", self.name, self.longitude, self.latitude)
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

impl Block {
    fn init(device_id: u32, from: Location, to: Location, previous_hash: String) -> Block {
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

impl Chain {
    fn init() -> Chain {
        return Chain { chain: Vec::new() };
    }
    
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
        if self.chain.last().unwrap().hash == b.previous_hash {
            return false;
        }

        // if no checks fail, then append the new block
        self.chain.push(b);
        return true;
    }
}

struct KeyLibrary {
    map: HashMap<String, VerifyingKey>,
}

impl KeyLibrary {
    fn init_empty() -> KeyLibrary {
        KeyLibrary {
            map: HashMap::new()
        }
    }

    fn init_from_file(path: String) -> Option<KeyLibrary> {
        let mut lib: KeyLibrary = KeyLibrary::init_empty();

        if let Ok(file) = File::open(path) {
            let reader = BufReader::new(file);

            for line_result in reader.lines() {
                if line_result.is_err() {
                    return None;
                }
                let line = line_result.unwrap();
                let vec: Vec<&str> = line.split(":").collect();
                let raw_bytes = hex::decode(vec[1]);
                if raw_bytes.is_err() {
                    return None;
                }
                let encoded_point = EncodedPoint::from_bytes(raw_bytes.unwrap());
                if encoded_point.is_err() {
                    return None;
                }
                let key = VerifyingKey::from_encoded_point(&encoded_point.unwrap());
                if key.is_err() {
                    return None;
                }
                lib.add_key(vec[0].to_string(), key.unwrap());
            }

            return Some(lib);
        }
        return None;
    }

    fn save(&self, path: String) -> bool {
        if let Ok(mut file) = File::create(path) {
            for (key, value) in &self.map {
                if file.write_all(key.as_bytes()).is_err() {
                    return false;
                }
                if file.write_all(b":").is_err() {
                    return false;
                }
                // convert VerifyingKey to file representation
                let encoded_point = value.to_encoded_point(false);
                // need to change encoding of it, as raw bytes cause errors
                let encoded_point_bytes = encoded_point.as_bytes();
                if file.write_all(hex::encode(encoded_point_bytes).as_bytes()).is_err() {
                    return false;
                }
                if file.write_all(b"\n").is_err() {
                    return false;
                }
            }
            return true;
        }
        return false;
    }

    fn add_key(&mut self, location: String, key: VerifyingKey) {
        self.map.insert(location, key);
    }

    fn verify(&mut self, location:String, msg: &[u8], signature: Signature) -> bool {
        if self.map.contains_key(&location) {
            return self.map[&location].verify(msg, &signature).is_ok();
        }
        return false;
    }
}

fn main() {
    let l: Location = Location {
        name: String::from("Oslo"),
        longitude: 5.7,
        latitude: 6.2,
    };

    let b1: Block = Block::init(0, l.clone(), l.clone(), String::from("genesis"));
    let b2: Block = Block::init(1, l.clone(), l.clone(), b1.hash.clone());

    let mut c: Chain = Chain::init();

    c.try_add_block(b1);
    c.try_add_block(b2);

    // println!("{}", c.chain[0].hash);
    // println!("{}", c.chain[1].hash);

    let signing_key: SigningKey = SigningKey::random(&mut OsRng);
    let verifying_key: VerifyingKey = signing_key.verifying_key().to_owned();
    println!("encoded point 1: {}", verifying_key.to_encoded_point(false));
    let vkey_point = verifying_key.to_encoded_point(true);
    let vkey_point_bytes = vkey_point.as_bytes();
    let encoded_point = EncodedPoint::from_bytes(vkey_point_bytes.clone()).unwrap();
    let result_read = VerifyingKey::from_encoded_point(&encoded_point);
    let verifying_key2: VerifyingKey = result_read.unwrap();

    println!("encoded point 2: {}", verifying_key2.to_encoded_point(false));
    let message = b"ECDSA proves knowledge of a secret number in the context of a single message";
    let signature: Signature = signing_key.sign(message);
    let is_correct = verifying_key.verify(message, &signature).is_ok();
    println!("signature is correct {}", is_correct);

    let mut lib: KeyLibrary = KeyLibrary::init_empty();
    lib.add_key(String::from("Oslo"), verifying_key);
    println!("verification with KeyLibrary {}", lib.verify(String::from("Oslo"), message, signature));
    lib.save(String::from("test.txt"));
    let lib2_option: Option<KeyLibrary> = KeyLibrary::init_from_file(String::from("test.txt"));
    if lib2_option.is_some() {
        let lib2: KeyLibrary = lib2_option.unwrap();
        lib2.save(String::from("test2.txt"));
    }
}