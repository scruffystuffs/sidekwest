use eyre::Result;
use serde::{Deserialize, Serialize};

pub struct MissingState;

pub trait TryDefault: Sized {
    fn default() -> Result<Self, MissingState> {
        Err(MissingState)
    }
}

impl<T: Default> TryDefault for T {
    fn default() -> Result<Self, MissingState> {
        Ok(Default::default())
    }
}

#[async_trait::async_trait]
pub trait Storable: for<'a> Deserialize<'a> + Serialize + Sized + Send + Sync {
    const STORAGE_KEY: &'static str;

    async fn fetch(engine: &impl StorageEngine) -> Self {
        todo!()
    }

    async fn save(&self, engine: &impl StorageEngine) -> Result<()> {
        todo!()
    }
}

#[async_trait::async_trait]
pub trait StorageEngine: Send {
    async fn load_state<S: Storable + Send + 'static>(&self) -> Result<S>;
    async fn save_state<S: Storable>(&self, data: &S) -> Result<()>;
}
