use std::path::PathBuf;

use eyre::Result;

use super::base::{Storable, StorageEngine};

pub struct LocalEngine {
    storage_dir: PathBuf,
}

impl LocalEngine {
    pub fn new(path: impl Into<PathBuf>) -> Self {
        Self {
            storage_dir: path.into(),
        }
    }

    fn resolve_filepath(&self, storage_key: &str) -> PathBuf {
        self.storage_dir.join(storage_key).with_extension(".json")
    }
}

#[async_trait::async_trait]
impl StorageEngine for LocalEngine {
    async fn load_state<S: Storable + 'static>(&self) -> Result<S> {
        let path = self.resolve_filepath(S::STORAGE_KEY);
        let result = tokio::task::spawn_blocking(move || {
            let file = std::fs::File::open(path)?;
            let reader = std::io::BufReader::new(file);
            let value: S = serde_json::from_reader(reader)?;
            Ok(value) as Result<S>
        })
        .await??;
        Ok(result)
    }

    async fn save_state<S: Storable>(&self, data: &S) -> Result<()> {
        let path = self.resolve_filepath(S::STORAGE_KEY);
        let contents = serde_json::to_vec(data)?;
        tokio::fs::write(path, contents).await?;
        Ok(())
    }
}
