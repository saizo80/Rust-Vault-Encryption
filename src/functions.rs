// Import external crates
use anyhow::anyhow;
use pyo3::prelude::*;
use sha2::{Digest, Sha256};
use std::{
    fs,
    fs::File,
    io::{self, BufRead, Write},
    path::Path,
    sync::atomic::{AtomicUsize, Ordering},
    thread,
    time::Duration,
};

// Import functions from other files
use crate::{encryptionFunctions, masterfile};

// Set static variable for later thread collection
//static GLOBAL_THREAD_COUNT: AtomicUsize = AtomicUsize::new(0);

///
/// Instantiate the argon2 config object
///
/// Returns `argon2::Config<'a>`
///
pub fn argon2_config<'a>() -> argon2::Config<'a> {
    argon2::Config {
        variant: argon2::Variant::Argon2id,
        hash_length: 32,
        lanes: 8,
        mem_cost: 16 * 1024,
        time_cost: 8,
        ..Default::default()
    }
}

///
/// Check whether the given path is a file.
/// # Arguments
/// - `path: &String`
///     - Path to be checked
///
/// Returns `bool`
///
pub fn check_file(path: &str) -> bool {
    fs::metadata(path).unwrap().file_type().is_file()
}

///
/// Check whether the given path is a directory
/// # Arguments
/// - `path: &String`
///     - Path to be checked
///
/// Returns `bool`
///
pub fn check_dir(path: &str) -> bool {
    fs::metadata(path).unwrap().file_type().is_dir()
}

///
/// Given a Vector (Vec<u8>), will return an Array [u8] of
/// appropriate size.
/// # Arguments
/// - `v: Vec<T>`
///     - Vector of generic type to be moved into Array
///
/// Returns `[T; N]`
///
pub fn into_array<T, const N: usize>(v: Vec<T>) -> [T; N] {
    v.try_into()
        .unwrap_or_else(|v: Vec<T>| panic!("Expected a Vec of length {} but it was {}", N, v.len()))
}

///
/// Main function for directory recursion. Will scan each directory for files and
/// directories. If a file is found it will be encrypted or decrypted depending on the
/// passed value for `force_encrypt`. If a directory is found, a new thread will be spawned
/// and the function will be recursively called with the updated path of the directory.
/// # Arguments
/// - `path: &String`
///     - The path of the directory to scan.
/// - `data: &masterfile::MasterfileData`
///     - The data of the decrypted masterfile.
///         - Masterkey for decryption/encryption
///         - Folder Nonce and Salt for directory name encryption/decryption
/// - `force_encrypt: bool`
///     - The bool will determine whether files are encrypted or decrypted.
///
/// Returns `Result<(), anyhow::Error>`
///
/*
pub fn dir_recur(
    path: &str,
    data: &masterfile::MasterfileData,
    force_encrypt: bool,
) -> Result<(), anyhow::Error> {
    let paths = fs::read_dir(path).unwrap();
    for path_inv in paths {
        let x = path_inv?.path().into_os_string().into_string().unwrap();
        if check_dir(&x) {
            // Clone data for moving to new thread
            let tx = x.clone();
            let tdata = data.clone();
            let tbool = force_encrypt;

            // Increment the global thread count
            GLOBAL_THREAD_COUNT.fetch_add(1, Ordering::SeqCst);
            thread::spawn(move || {
                dir_recur(&tx, &tdata, tbool).unwrap();

                // Once recursion is finished, decrement the global thread count
                GLOBAL_THREAD_COUNT.fetch_sub(1, Ordering::SeqCst);
            });
        } else {
            // If the path is a file, decrypt or encrypt depending on the passed
            // bool `force_encrypt`
            if !x.ends_with("masterfile.e") && !x.ends_with(".DS_Store") && !x.ends_with("Icon") {
                if x.ends_with(".encrypted") && !force_encrypt {
                    encryptionFunctions::decrypt_file(&x, &data.master_key).ok();
                } else if !x.ends_with(".encrypted") && force_encrypt {
                    encryptionFunctions::encrypt_file(&x, &data.master_key).ok();
                }
            }
        }
    }
    Ok(())
}
*/

///
/// Function for encrypting/decrypting directory names. This cannot be called
/// during the initial recursion of the directory tree due to the multithreading.
/// Some threads will finish before others, and will change the directory name, preventing
/// other threads from finished due to the incorrect path.
/// # Arguments
/// - `path: &String`
///     - Path to the directory
/// - `data: &masterfile::MasterfileData`
///     - Data from the decrypted masterfile
/// - `force_encrypt: bool`
///     - Determines whether to encrypt or decrypt
///
/// Returns `Result<(), anyhow::Error>`
///
fn folder_recur(
    path: &str,
    data: &masterfile::MasterfileData,
    force_encrypt: bool,
) -> Result<(), anyhow::Error> {
    let paths = fs::read_dir(path).unwrap();
    for path_inv in paths {
        let x = path_inv?.path().into_os_string().into_string().unwrap();
        if check_dir(&x) {
            folder_recur(&x, data, force_encrypt)?;
            if x.ends_with(".encrypted") && !force_encrypt {
                encryptionFunctions::decrypt_foldername(&x, data)?;
            } else if !x.ends_with(".encrypted") && force_encrypt {
                encryptionFunctions::encrypt_foldername(&x, data)?;
            }
        }
    }
    Ok(())
}

#[pyfunction]
pub fn lock_vault(
    masterfile_path: String,
    dirs: Vec<String>,
    files: Vec<String>,
    password: String,
) -> PyResult<()> {
    let masterfile_data = masterfile::read_masterfile(&masterfile_path[..], &password[..]).unwrap();
    println!("Masterfile Read");
    static GLOBAL_THREAD_COUNT: AtomicUsize = AtomicUsize::new(0);
    for file_path in files {
        GLOBAL_THREAD_COUNT.fetch_add(1, Ordering::SeqCst);
        thread::spawn(move || {
            encryptionFunctions::encrypt_file(&file_path[..], &masterfile_data.master_key).unwrap();

            // Once recursion is finished, decrement the global thread count
            GLOBAL_THREAD_COUNT.fetch_sub(1, Ordering::SeqCst);
        });
    }
    while GLOBAL_THREAD_COUNT.load(Ordering::SeqCst) != 0 {
        thread::sleep(Duration::from_millis(1));
    }
    Ok(())
}

///
/// Function for unlocking/locking of a vault. Will call multiple functions
/// to go through the directory tree.
/// # Arguments
/// - `masterfile_path: String`
///     - Path to the masterfile
/// - `force_encrypt: bool`
///     - Determines whether to encrypt or decrypt
///
/// Returns `Result<(), anyhow::Error>`
///
/*
pub fn unlock_lock_vault(
    masterfile_path: String,
    force_encrypt: bool,
    stored_hash: Vec<u8>,
) -> Result<(), anyhow::Error> {
    // Get password and hash
    let password = get_password_input("Enter vault password: ")?;
    let hashed_password = hash_password_vec(password.clone())?;

    // Check if hash matches what is stored
    if hashed_password != stored_hash {
        return Err(anyhow!("Password does not match stored password"));
    }
    // Read in the data from the masterfile and store in a data structure
    let masterfile_data = masterfile::read_masterfile(&masterfile_path, &password)?;

    // Get the top of the directory tree
    let top_dir_path = masterfile_path
        .strip_suffix("/masterfile.e")
        .unwrap()
        .to_string();

    // This process tends to take some time so print the process steps
    // out in the terminal
    if force_encrypt {
        println!("Encrypting Files");
    } else {
        println!("Decrypting Files");
    }

    // Recurse through the directory tree
    dir_recur(&top_dir_path, &masterfile_data, force_encrypt)?;

    // Wait for all threads to be finished recurssing
    while GLOBAL_THREAD_COUNT.load(Ordering::SeqCst) != 0 {
        thread::sleep(Duration::from_millis(1));
    }

    // Print process of foldernames
    if force_encrypt {
        println!("Encrypting Foldernames");
    } else {
        println!("Decrypting Foldernames");
    }

    // Encrypt/decrypt foldernames
    folder_recur(&top_dir_path, &masterfile_data, force_encrypt)?;

    Ok(())
}
*/

#[pyfunction]
pub fn hash_password_string(password: String) -> PyResult<String> {
    // Get hash of password
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    Ok(hex::encode(hasher.finalize()))
}

pub fn hash_password_vec(password: String) -> Result<Vec<u8>, anyhow::Error> {
    // Get hash of password
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    Ok(hex::decode(hex::encode(hasher.finalize()))?)
}
