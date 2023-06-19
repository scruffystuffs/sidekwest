use std::path::PathBuf;

use eyre::Result;
use serde::{Deserialize, Serialize};

use self::base::{Storable, StorageEngine};

mod base;
mod local_file;

pub struct Storage {
    local: Option<local_file::LocalEngine>,
}

impl Storage {
    pub async fn save_state(&self, data: &impl Storable) -> Result<()> {
        if let Some(local) = &self.local {
            data.save(local).await?;
        }
        Ok(())
    }
}
