#![allow(non_snake_case)]
#![allow(dead_code)]
#![allow(unused_imports)]
use pyo3::prelude::*;

mod encryptionFunctions;
mod functions;
mod masterfile;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn Rust_Vault_Encryption(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(functions::hash_password_string, m)?)?;
    m.add_function(wrap_pyfunction!(functions::lock_vault, m)?)?;
    m.add_function(wrap_pyfunction!(masterfile::create_masterfile, m)?)?;
    m.add_function(wrap_pyfunction!(functions::unlock_vault, m)?)?;
    Ok(())
}
