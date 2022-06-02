# Rust Vault Encryption

## About

This program is meant to create '*vaults*' that are at the top of a directory tree and can encrypt and decrypt the files and folders therein. The masterfile, named *masterfile.e* is encrypted with the vault password, and holds all the information to encrypt and decrypt the vault files and foldernames. The masterfile's contents are never written to the disk unencrypted, even during creation. The contents are only decrypted into memory, and are zeroized when finished being used.

It needs to be said that this program is written for UNIX systems, MacOS and Linux, and has **not** been tested and will most likely **not** work on Windows.

Also this is just a personal project to learn the rust language. Please do **not** use this program for serious encryption. If you are in need of that please use an app like Cryptomator, which is what I personally use.
